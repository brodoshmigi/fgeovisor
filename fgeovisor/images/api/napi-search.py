import napi
from gdal_staff import gdal_rast_handler

import time
import uuid
import datetime

import numpy as np
import pandas as pd

import pystac as stac
from pystac_client.client import Client

from typing import (
    Optional,
    List,
    Dict,
    Set,
    Tuple,
    Generator
    )


"""
    Способ взаимодействия с geospatial через stac
    # stac требует авторизации для предоставление расширенного доступа
"""
# https://pystac-client.readthedocs.io/en/stable/api.html
# https://pystac.readthedocs.io/en/latest/api.html


# TODO Нужно рассмотреть и по возможности применить
# 1. Repository pattern for data access
# 2. Implement Strategy Pattern for search alg
# 3. Command Pattern for download op
# Это поможет сделать структуру более абстрактной
# И, соответственно, расширяемой и тестируемой
# Будет проще понять и простить
# Правда почему-то время испортилось и теперь оно 15 сек на поиск, а не 10, как раньше
# Еще нужно добавить асинхронку в download, это ускорит процесс очень сильно
# Да и в принципе асинхронку если везде куда лезет добавить, будет норм
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

    def get_sort_childs(self, catalog_list: List[str]):
       return {link.get_href() for link in self.get_search_links() if link.title in catalog_list}

class ClientPool:

    def __init__(self):
        self.clients = {}

    def get_client(self, link: str) -> Client:
        if link not in self.clients:
            self.clients[link] = Client.open(link)
        return self.clients[link]

class SearchEngine():
    
    def __init__(
            self, 
            satelite_names: List[str] = ['landsat'],
            catalog_list: List[str] = None
            ):
        self.satelite_names = satelite_names
        self.catalog_list = catalog_list
        self.catalog = SearchCatalog().get_sort_childs(self.catalog_list)
        self.client_pool = ClientPool()
    
    def search_org_catalogs(
            self, 
            area: Tuple | List = None, 
            date: str = None
            ) -> pd.DataFrame:
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
        for link in self.catalog:
            client = self.client_pool.get_client(link)
            collections = client.collection_search(
                q='landsat',
                bbox=area,
                datetime=date
                )
            data = pd.DataFrame([
                {
                    'id': c['id'],
                    'href': link
                } 
                for c in collections.collections_as_dicts()
            ])
            filtered = data[data['id'].str.lower().apply(
                        lambda x: any(search in x for search in SEARCH_LIST))]
            true_collections = pd.concat([true_collections, filtered])
        return true_collections

    def get_items(self,
                  collections: Optional[pd.DataFrame] = None,
                  date: str = None,
                  area: Tuple | List = None,
                  orderby: Dict = None,
                  max_items: int = None
                  ):
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
            items = self.client_pool.get_client(link)
            item_search = items.search(
                max_items=max_items,
                collections=ids,
                bbox=area,
                datetime=date,
                limit=50,
                query={"eo:cloud_cover": {"lt": 10}}
                )
            data = np.array([item['assets']['B04']['href']
                              for item in item_search.items_as_dicts()])
            yield data

class DBChecker():
    pass

class ISearch():
    
    def __init__(
            self,
            session: napi.NasaAPIBase = None,
            ):
        self.session = session.session()

        self.session.create_session()

    def search(
            self,
            satelite_names: List[str] = None,
            catalog_list: List[str] = None
            ) -> SearchEngine:
        return SearchEngine(satelite_names, catalog_list)
    
    def download_image(
            self, 
            item_href: str, 
            name: str = None
            ) -> str | int:
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

        response = self.session.request(
            "GET", 
            url=item_href, 
            stream=True, 
            allow_redirects=True)
        
        if response.status_code == 200:
            gdal_rast_handler(response.raw.data, image_name=name)
            return 'Complete'
        else: 
            return response.status_code
        

# Нужно сделать разделение по функциональности.
# Скачать и искать это разные функциональности.
# Проверка или взаимодействие с Базами данных это разная функциональность.
# И общий интерфейс для взаимодействия со всем этим добром.
'''
if __name__ == '__main__':
    config = napiF.NasaAPIConfig('shii', '6451Yyul1234/')
    base = napiF.NasaAPIBase(config=config)

    base = ISearch(session = base)
    
    api = base.search(
        catalog_list = ['USGS_LTA', 'LPDAAC_ECS', 'LPCLOUD', 'ESA'],
        satelite_names = ['landsat', 'hlsl', 'sentinel', 'hlss']
        )

    dt = api.search_org_catalogs(
        area=(42.171192, 45.04739, 42.18441, 45.053151),
        date='2024-09/2024-11'
        )
    
    time2 = time.perf_counter()
    print(f'{dt} \n {time2 - time1:0.4f}')

    links = api.get_items(collections=dt, max_items=1)

    for i in links:
        print(i)

    time3 = time.perf_counter()
    print(f'{time3 - time1:0.4f}')
'''