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

import auth
from gdal_staff import tif_creator


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
    """
    Здесь нужно будет добавить входящими аргументы.

    Но это необходимо только, если собираемся использовать более низкий уровень
    библиотеки pystac_client.
    """

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

        response = http.get(url=kwargs['url'],
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

    def __init__(self, session: auth.NasaAPIBase):
        # TODO поумнее нужно сделать
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
    """
    Есть одна вещая проблема.

    Client возвращает результат и мы уже определились, что для ассетов и коллекций,
    как минимум, у наса, должны быть разные link. Но, в чем же все таки проблема?
    
    Когда эта библиотека возвращает результат - он представляется ввиде объекта,
    т.к. содержит в себе кучу разных страниц с результатами, да, именно страниц.

    Это еще ничего, однако, получение таким образом результата превращается в
    <class ...>, что нас не интересует, так как нам из всех этих резульатов нужен,
    конечно, если нужен, тот, который подойдет под наши запросы. Объясняю почему:

    Если наша Q в поиске(кто не знаком с большой Q, просто знайте, это свободный параметр)
    будет равна landsat он выдаст абсолютно все коллекции, где хоть раз упоминалось это слово
    кто наблюдательный должен уже понять, что там содержится не только landsat,
    а, например, его смежные миссии, которые, соответственно, нам уже не подходят.

    Почему же не подходят? Мы ищем только те, которые содержат в себе каналы с 1 по 9.
    Но и не только это, еще, конечно, хотелось бы получать более точные результаты,
    а не все, что есть... Тем более там могут быть коллекции, которые уже морально устарели.
    Чисто логически, мы могли бы и не сортировать вообще ничего, получив коллекции, просто,
    скажем так, искать вхождения, да - это проблему бы решило, но мы, таким образом,
    можем и не попасть в то, что нам нужно.

    Ввиду чего возникает необходимость сортировки этих объектов по id, а это
    можно сделать только если использовать collections_as_... и все бы ничего,
    но авторы библиотеки реализовали эту функции как генератор, из-за чего,
    чтобы получить результат, нужно использовать очень большое количество циклов,
    что увеличивает время на совершение запроса.

    Да, может многопоточка это фиксит, но синхронная версия будет медленной ввиду этого.

    И эту проблему нужно решить, либо расширением существующего класса нашего,
    либо другими фокусами, конечно, можно ничего и не менять. Разница 1-3 сек.
    Ну либо можно получать равки и отправлять в другой класс, который уже будет фильтровать.
    """

    def __init__(self,
                 satelite_names: List[str] = ['landsat'],
                 catalog_list: List[str] = None,
                 clients_pool=None):
        self.satelite_names = set(satelite_names)
        self.catalog = SearchCatalog().get_sort_childs(orderby=catalog_list)
        self.clients_pool = clients_pool

    def get_by_orgs(self,
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
        for link in self.catalog:
            data = pd.DataFrame([{
                'id': c['id'],
                'href': link
            } for c in self._search_collection(
                link=link, bbox=area, datetime=date)])
            filtered = data[data['id'].str.lower().apply(
                lambda x: any(search in x for search in self.satelite_names))]
            true_collections = pd.concat([true_collections, filtered])
        return true_collections
    
    def get_by_link(self):
        for link in self.catalog:
            return self._get_collections(link=link)

    def _search_collection(self, link: str, **kwargs):
        client: Client = self.clients_pool.get_client(link=link)
        collections = client.collection_search(q='landsat', **kwargs)
        return collections.collections_as_dicts()

    def _get_collections(self, link: str):
        # Маленький шаг для человека, но огромный для меня
        # Большее понимание библиотеки находится здесь...
        client: Client = self.clients_pool.get_client(link=link)
        result = pd.DataFrame([{
            'r': c.id,
            'link': link,
        } for c in client.get_collections()])
        return result.drop_duplicates()
    
    def _get_collection(self, link: str, id: str):
        client: Client = self.clients_pool.get_client(link=link)
        result = pd.DataFrame([{
            'r': c.id,
            'link': link,
        } for c in client.get_collection(id)])
        return result

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
    def get(self, collections, **kwargs) -> Generator[Any, Any, Any]:
        # -> pd.Dataframe() желательно
        # т.к. возвращать хочется больше инфы, чем просто ссылки
        # Но у нас тут еще и yield)
        true_collections = collections
        links = true_collections['href'].drop_duplicates().tolist()
        ids = true_collections['id'].tolist()
        for link in links:
            items = self._get_assets(link=link, ids=ids, **kwargs)
            data = np.array([
                item['assets']['B04']['href']
                for item in items.items_as_dicts()
            ])
            yield data

    def _get_assets(self, link: str, ids, **kwargs):
        items: Client = self.clients_pool.get_client(link=link)
        item_search = items.search(collections=ids,
                                   limit=50,
                                   query={"eo:cloud_cover": {
                                       "lt": 10
                                   }},
                                   **kwargs)
        return item_search


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

    def loader(self, sauth) -> IDownload:
        return IDownload(sauth)