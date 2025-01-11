from django.contrib.gis.gdal.raster.source import GDALRaster

from typing import (Optional, List, Set, Generator, Tuple, Dict, Any)
import time
import uuid
import datetime
from functools import lru_cache
from abc import ABC, abstractmethod

import urllib3
import requests
import numpy as np
import pandas as pd
import pystac as stac
from pystac_client.client import Client

import napi

time1 = time.perf_counter()


def tif_creator(*args: str, image_name: str) -> GDALRaster:
    """
    Создает .tif файл из виртуальных .tif файлов

    Или может создать один .tif с несколькими каналами из нескольких .tif с одним каналом

    Args:
        *args (str):
            Принмает в себя ссылки на .tif файл.
        image_name (str):
            Задает имя снимку исходя из даты его создания
    Returns:
        Image (byte or .tif):
            Возвращает созданный/объединенный .tif новым файлов
            и в течении сессии сохраняется в оперативной памяти.
    """
    if not args:
        raise ValueError('At least one .tif file is required.')
    

    img_list_handler = [GDALRaster(value) for value in args]

    source = img_list_handler[0]
    source_driver = source.driver

    # Issue - в архивах могут быть снимки без ха-ха srid...
    if not source.srid:
        raise ValueError('Snimok xuini, url ne to')

    # в name указывается имя директории, в которую сохранится файл
    raster_create = GDALRaster({
        'srid': source.srid,
        'width': source.width,
        'height': source.height,
        'driver': str(source_driver),
        'name': f'{str(image_name)}.tif',
        'datatype': source.bands[0].datatype(),
        'nr_of_bands': len(img_list_handler)
    })

    for y in range(len(img_list_handler)):
        raster_create.bands[y].data(img_list_handler[y].bands[0].data())

    #return raster_create


class SearchCatalog():

    def __init__(self, href: str = 'https://cmr.earthdata.nasa.gov/stac'):
        # href сохраняется в self.root_catalog
        self.stack_obj = stac.Link('root', href).resolve_stac_object()
        self.root_catalog = stac.Catalog.from_file(self.stack_obj)

    def __str__(self) -> str:
        return f'ID: {self.root_catalog.id},\
                \n |Title: {self.root_catalog.title}\
                \n |Desciption: {self.root_catalog.description}'

    def get_catalog(self) -> stac.Catalog:
        return self.root_catalog

    def get_search_links(self) -> Set[stac.Link]:
        return set(self.root_catalog.get_child_links())

    def get_links_titles(self) -> Generator[str, str, str]:
        for link in self.get_search_links():
            yield link.title

    # это хренота пока не работает, но думаю если setter добавить оно пойдет
    def _get_satelite_name(self):
        if type(self.satelite_names) == type([]):
            return self.satelite_names[0]
        else:
            return self.satelite_names

    def get_sort_childs(self, orderby: List[str]):
        return {
            link.get_href()
            for link in self.get_search_links() if link.title in orderby
        }


class ClientPool():

    def __init__(self):
        self.clients = {}

    @lru_cache(maxsize=32)
    def get_client(self, link: str) -> Client:
        if link not in self.clients:
            self.clients[link] = Client.open(link)
        return self.clients[link]


class Download(ABC):

    @abstractmethod
    def download(self):
        pass


class SyncDownload(Download):

    def download(self, **kwargs):

        http: requests.Session = kwargs['session']

        response = http.request("GET",
                                url=kwargs['url'],
                                stream=True,
                                allow_redirects=True,
                                timeout=30)

        if response.status_code == 200:
            tif_creator(response.raw.data, image_name=kwargs['name'])
            return 'Complete'
        else:
            return response.status_code


class AsyncDownload(Download):

    def download(self, **kwargs):
        pass


class IDownload():

    def __init__(self, session: napi.NasaAPIBase):
        self.base = session.session()

        self.base.create_session()
        self.session = self.base.get_session()

    def download(self, url: str, name: str):
        return SyncDownload().download(session=self.session,
                                       url=url,
                                       name=name)

    def adownload(self, item_href: str, name: str = None):
        return AsyncDownload().download(item_href=item_href, name=name)


class SearchCollections():

    def __init__(self,
                 satelite_names: List[str] = ['landsat'],
                 catalog_list: List[str] = None,
                 clients_pool=None):
        self.satelite_names = set(satelite_names)
        self.catalog = SearchCatalog().get_sort_childs(orderby=catalog_list)
        self.clients_pool = clients_pool

    def get_org_catalogs(self,
                         area: Tuple | List = None,
                         date: str = None) -> pd.DataFrame:
        """
        **Ищет каталоги, которые соответствуют нашему запросу.**
        
        Способы оптимизации:
            - Указание способов фильтрации в параметрах /search
            - Использование Pandas

        Returns:
            Dataframe ('id' | 'href'):
                DataFrame с отсортированными коллекциями
        """
        true_collections = pd.DataFrame()
        #collections_list = []
        for link in self.catalog:
            client: Client = self.clients_pool.get_client(link)
            collections = client.collection_search(q='landsat',
                                                   bbox=area,
                                                   datetime=date)
            data = pd.DataFrame([{
                'id': c['id'],
                'href': link
            } for c in collections.collections_as_dicts()])
            filtered = data[data['id'].str.lower().apply(
                lambda x: any(search in x for search in self.satelite_names))]
            true_collections = pd.concat([true_collections, filtered])
        return true_collections


class Assets(ABC):

    @abstractmethod
    def get(self) -> Generator[Any, Any, Any]:
        """
        **Ищет объекты, которые соответствуют нашему запросу.**
            
        Способы оптимизации:
            - Указание способов фильтрации в параметрах /search
            - Использование Numpy

        Args:
            inersects (GeoJson or Dict GeoJsonLike):
                Создает область интереса для поиска объектов
            query (List of JSON query params):
                Фильтрует изображения по заданым параметрам (ускоряет в 2 раза)
            max_items (int):
                Количество объектов, которое необходимо получить.

                Чем ближе значение к 1, или =1, тем быстрее выполняется скрипт. 

        Returns:
            Iterator (NDarray[Any]):
                Возвращает iterator с numpy массивом из объектов
        """
        pass


class SyncSearchAssets(Assets):

    def __init__(self, clients_pool):
        self.clients_pool = clients_pool

    # Параметры можно заменить на словарь
    def get(self, **kwargs) -> Generator[Any, Any, Any]:
        # -> pd.Dataframe() желательно
        # т.к. возвращать хочется больше инфы, чем просто ссылки
        # Но у нас тут еще и yield)
        true_collections = kwargs['collections']
        kwargs.pop('collections')
        links = true_collections['href'].drop_duplicates().tolist()
        ids = true_collections['id'].tolist()
        for link in links:
            items = self.clients_pool.get_client(link)
            item_search = items.search(collections=ids,
                                       limit=50,
                                       query={"eo:cloud_cover": {
                                           "lt": 10
                                       }},
                                       **kwargs)
            data = np.array([
                item['assets']['B04']['href']
                for item in item_search.items_as_dicts()
            ])
            yield data


class AsyncSearchAssets(Assets):

    def __init__(self, clients_pool):
        self.clients_pool = clients_pool

    def get(self, **kwargs) -> Generator[Any, Any, Any]:
        pass


class SearchEngine():

    def __init__(self, clients_pool):
        self.assets = SyncSearchAssets(clients_pool=clients_pool)
        self.aassets = AsyncSearchAssets(clients_pool=clients_pool)

    #SyncSearchAssets
    def get_assets(self,
                   collection: Optional[pd.DataFrame] = None,
                   date: str = None,
                   area: Tuple | List = None,
                   orderby: Dict = None,
                   max_items: int = None):
        return self.assets.get(collections=collection,
                               datetime=date,
                               bbox=area,
                               max_items=max_items)

    #AsyncSearchAssets
    def aget_assets(self):
        return self.aassets.get()


class ISearch():

    def __init__(self):
        self.clients_pool = ClientPool()

    # Нужно более глубоко здесь проработать логику стратегии
    # Чтобы просто тыкнул и все заработало
    def search_collections(
            self,
            sat_names: List[str] = None,
            catalog_filter: List[str] = None) -> SearchCollections:

        return SearchCollections(satelite_names=sat_names,
                                 catalog_list=catalog_filter,
                                 clients_pool=self.clients_pool)

    def search_items(self) -> SearchEngine:
        return SearchEngine(clients_pool=self.clients_pool)

    def loader(self, base) -> IDownload:
        return IDownload(base)