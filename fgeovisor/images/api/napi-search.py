from django.contrib.gis.gdal.raster.source import GDALRaster

import napi

import time
import uuid
import datetime

import urllib3

import requests

import numpy as np
import pandas as pd

import pystac_client
import pystac as stac
from pystac_client.client import Client

from typing import Optional
from functools import lru_cache


'''
Способ взаимодействия с geospatial через stac
# stac требует авторизации для предоставление расширенного доступа
'''
# https://pystac-client.readthedocs.io/en/stable/api.html
# https://pystac.readthedocs.io/en/latest/api.html


def gdal_rast_handler(*args: str, image_name: str) -> GDALRaster:
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

    # в name указывается имя директории, в которую сохранится файл
    raster_create = GDALRaster(
        {
            'srid': source.srid,
            'width': source.width,
            'height': source.height,
            'driver': str(source_driver),
            'name': f'{str(image_name)}.tif',
            'datatype': source.bands[0].datatype(),
            'nr_of_bands': len(img_list_handler),
        }
    )

    for y in range(len(img_list_handler)):
        raster_create.bands[y].data(img_list_handler[y].bands[0].data())
    
    return raster_create

class ImageFromCMRStac:
    
    def __init__(self, href = 'https://cmr.earthdata.nasa.gov/stac', 
                 satelite_names: list = ['landsat'], 
                 bbox: list[float] = None, 
                 datetime: str = None, 
                 catalog_list: list = None,
                 session = requests.Session):
        """
        **Класс поиска и загрузи .tif файлов из CMR NASA**

        Оптимизация:
            - Ускорение при помощи Pandas|Numpy
            - Указание правильных параметров для /search
            - Использование SQL... process

        Args:
            href (str):
                RU: Ссылка на ***Родительский*** **стак** файл(каталог), может быть как **http(s)://** так и **C:/**
                - пример: https://cmr.earthdata.nasa.gov/stac
            satelite_names (list):
                RU: ищет по имени спутника
                - пример: landsat, hlsl, sentinel, hlss
            bbox (list):
                RU: Указывает зону интереса
                - обычно список или кортеж, но желательно GEOJSON
            datetime (datetime):
                RU: указывает время для поиска по нему
                - указываем год: ищет за весь год
                - указываем год и месяц: ищет за весь месяц в этом году
                - указываем год, месяц и день: ищет за весь день в этом месяце этого года
                - пример за 3 месяца 2024-09/2024-11
            catalog_list (list):
                RU: список организаций для поиска по ним
        """
        self.href = stac.Link('root', href)
        self.satelite_names = satelite_names
        self.bbox = bbox
        self.datetime = datetime
        self.catalog_list = catalog_list
        # Создаем экземпляр pystac.Catalog
        self.stack_obj = self.href.resolve_stac_object()
        self.root_catalog = stac.Catalog.from_file(self.stack_obj)
        self.session = session

    def __str__(self):
        return f'ID: {self.root_catalog.id},\
                \n |Title: {self.root_catalog.title}\
                \n |Desciption: {self.root_catalog.description}'
                
    def get_root_catalog(self):
        return self.root_catalog
    
    def get_childs(self):
        return set(self.root_catalog.get_child_links())
    
    def get_childs_titles(self):
        for link in self.get_childs():
            yield link.title

    @lru_cache(maxsize=None)
    def _open_client(self, link):
        return Client.open(link)
    
    def _get_childs(self):
       return {link.get_href() for link in self.get_childs() if link.title in self.catalog_list}
            
    # это хренота пока не работает, но думаю если setter добавить оно пойдет
    def _get_satelite_name(self):
        if type(self.satelite_names) == type([]):
            return self.satelite_names[0]
        else:
            return self.satelite_names

    def search_org_catalogs(self):
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
        SEARCH_LIST = set(map(lambda x: x, self.satelite_names))
        for link in self._get_childs():
            collections_client = self._open_client(link)
            search_collections = collections_client\
                                .collection_search(q='landsat',
                                                bbox=self.bbox,
                                                datetime=self.datetime)
            data = pd.DataFrame([
                {
                    'id': collection['id'],
                    'href': link
                } for collection in search_collections.collections_as_dicts()
            ])
            filtered = data[data['id'].str.lower().apply(
                        lambda x: any(search in x for search in SEARCH_LIST))]
            true_collections = pd.concat([true_collections, filtered])
        return true_collections

    def get_items(self,
                  collections: Optional[pd.DataFrame] = None, 
                  intersect: str|dict = None, 
                  query: dict = None,
                  max_items: int = None):
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
        true_collections = collections
        links = true_collections['href'].drop_duplicates().tolist()
        ids = true_collections['id'].tolist()
        for link in links:
            items = self._open_client(link)
            item_search = items.search(
                max_items=max_items,
                collections=ids,
                bbox=self.bbox,
                datetime=self.datetime,
                limit=50,
                query={"eo:cloud_cover": {"lt": 10}}
                )
            data = np.array([item['assets']['B04']['href']
                              for item in item_search.items_as_dicts()])

            yield data

    def download_image(self, 
                       item_href: str, 
                       name: str = None,):
        """
        **Скачивает изображение по выданному ссылке(в будущем по выданному ассету или объекту)**

        Сейчас время выполнения для одного изображения 6 сек. 
        (используя get_items(max_items = 1))

        Полное время выполнения, включая search_org_catalogs и get_items() - больше минуты.
        Но, это с учетом того, что скачивается больше 20 изображений  

        Args:
            item_href (str):
                Принимает в себя ссылку на изображение, однако, именно на конретное (uri)
            name (str):
                Место для сохранения изображения.

        Returns:
            Image (byte):
                Возвращает сообщение о успешном скачивании и скачивает изображение в директорию
        """

        # ### Нужно еще на забыть указать здесь папку
        response = self.session.request("GET", url=item_href, stream=True, allow_redirects=True)
        if response.status_code == 200:
            gdal_rast_handler(response.raw.data, image_name=name)
            return 'Complete'
        else: 
            return response.status_code
        
    def save_catalog(self):
        """
        **Нужно для сохранения данных в локальный репозиторий. SQL.**
        """
        pass

    def check_catalog_contains_in_uri(self):
        """
        **Функция проверки существует ли каталог в нашем локальном репозитории.**
        """
        pass

    def search_interface(self):
        """
        **Объединенный интерфейс вызова функций.**
        Нужен, чтобы проверять условия и вызывать соответствующие функции.
        """
        pass