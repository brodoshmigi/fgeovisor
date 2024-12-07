import ee 
import time
import urllib3
import datetime
import requests
import numpy as np
import pandas as pd
import pystac_client
import pystac as stac
from functools import lru_cache
from typing import Optional
from pystac_client.client import Client
from os import (makedirs, remove, path, listdir, rmdir)
from django.contrib.gis.gdal.raster.source import GDALRaster
from zipfile import ZipFile
from numpy import seterr, nanmax
from .models import Image
from matplotlib.pyplot import(imshow, imsave)
from matplotlib import use
from polygons.serializators import PolygonFromDbSerializer


ee.Authenticate()
ee.Initialize(project='ee-cocafin1595')
IMAGE_DIR = path.dirname(path.abspath(__file__)) + '/IMAGES'


class Image_From_GEE():
    
    def __init__(self, polygon,
                  date_start='2023-01-01', date_end=str(datetime.date.today())):
        self.polygon = polygon
        self.coords = ee.Geometry.Polygon(PolygonFromDbSerializer(polygon).data['geometry']['coordinates'])
        self.dir = IMAGE_DIR + ('/image' + str(len(listdir(IMAGE_DIR)) + 1))
        self.date_start = date_start
        self.date_end = date_end
    
    def get_download_url(self):
        sentinel_image = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED') \
            .filterDate(self.date_start, self.date_end) \
            .filterBounds(self.coords) \
            .filter(ee.Filter.lt('CLOUD_COVERAGE_ASSESSMENT', 10)) \
            .select(['B4', 'B8']) \
            .first()
        return sentinel_image.clip(self.coords).getDownloadURL()

    def download_image(self):
        response = requests.get(self.get_download_url())
        path = self.dir + '.zip'
        with open(path, 'wb') as fd:
            fd.write(response.content)
        extract_to_directory = path.replace('.zip', '')
        makedirs(extract_to_directory)
        with ZipFile(path, 'r') as zip_ref:
            zip_ref.extractall(extract_to_directory)
        remove(path)

    def visualization(self):
        list_of_rasters = listdir(self.dir)
        red = GDALRaster(self.dir + '/' + list_of_rasters[0]).bands[0].data()
        nir = GDALRaster(self.dir + '/' + list_of_rasters[1]).bands[0].data()
        seterr(divide='ignore', invalid='ignore')
        ndvi = (nir - red) / (nir + red) 
        ndvi = ndvi / nanmax(ndvi)
        use('agg')
        valid_array = imshow(ndvi).get_array()
        imsave((self.dir + '.png'), valid_array)
        image_DB = Image(polygon=self.polygon, url=(self.dir + '.png'))
        image_DB.save()
        remove(self.dir + '/' + listdir(self.dir)[0])        
        remove(self.dir + '/' + listdir(self.dir)[0])
        rmdir(self.dir)


class ImageFromCMRStac:
    
    def __init__(self, href = 'https://cmr.earthdata.nasa.gov/stac', 
                 satelite_names: list = ['landsat'], bbox: list[float] = None, 
                 datetime: str = None, catalog_list: list = None):
        """
        **Класс поиска и загрузи .tif файлов из CMR NASA**

        Оптимизация:
            - Ускорение при помощи Pandas|Numpy
            - Указание правильных параметров для /search
            - Использование SQL... process

        Args:
            href (href):
                RU: Ссылка на ***Родительский*** **стак** файл(каталог), может быть как **http(s)://** так и **C:/**
                - пример: https://cmr.earthdata.nasa.gov/stac
            satelite_names (satelite_names):
                RU: ищет по имени спутника
                - пример: landsat, hlsl, sentinel, hlss
            bbox (bbox):
                RU: Указывает зону интереса
                - обычно список или кортеж, но желательно GEOJSON
            datetime (datetime):
                RU: указывает время для поиска по нему
                - указываем год: ищет за весь год
                - указываем год и месяц: ищет за весь месяц в этом году
                - указываем год, месяц и день: ищет за весь день в этом месяце этого года
                - пример за 3 месяца 2024-09/2024-11
            catalog_list (catalog_list):
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
        return Client.from_file(link)
    
    def _get_childs(self):
       return {link.get_href() for link in self.get_childs() if link.title in self.catalog_list}
            
    # это хренота пока не работает, но думаю если setter добавить оно пойдет
    def _get_satelite_name(self):
        if type(self.satelite_name) == type([]):
            return self.satelite_name[0]
        else:
            return self.satelite_name

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
            true_collections = pd.concat([true_collections, 
                                          filtered['id'],
                                          filtered['href']])
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
        links = true_collections['href'].drop_duplicates().dropna().tolist()
        ids = true_collections['id'].dropna().tolist()
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

    def download_image(self, item_href: str, DIR_NAME: str = None):
        """
        **Скачивает изображение по выданному ссылке(в будущем по выданному ассету или объекту)**

        Сейчас время выполнения для одного изображения 6 сек. 
        (используя get_items(max_items = 1))

        Полное время выполнения, включая search_org_catalogs и get_items() - больше минуты.
        Но, это с учетом того, что скачивается больше 20 изображений  

        Args:
            item_href (str):
                Принимает в себя ссылку на изображение, однако, именно на конретное (uri)
            DIR_NAME (str):
                Место для сохранения изображения.

        Returns:
            Image (byte):
                Возвращает сообщение о успешном скачивании и скачивает изображение в директорию

        """
        # Истекает через 2 месяца
        token = 'eyJ0eXAiOiJKV1QiLCJvcmlnaW4iOiJFYXJ0aGRhdGEgTG9naW4iLC'\
        + 'JzaWciOiJlZGxqd3RwdWJrZXlfb3BzIiwiYWxnIjoiUlMyNTYifQ'\
        + '.eyJ0eXBlIjoiVXNlciIsInVpZCI6InNoaWkiLCJleHAiOjE3Mzc4MDExMDIsImlhdCI6MT'\
        + 'czMjYxNzEwMiwiaXNzIjoiaHR0cHM6Ly91cnMuZWFydGhkYXRhLm5'\
        + 'hc2EuZ292IiwiaWRlbnRpdHlfcHJvdmlkZXIiOiJlZGxfb3BzIiwiYXNzdXJhbmNlX2xldmV'\
        + 'sIjoyfQ.LY5M0ZCD_Hjf64Gz2orXfozI0RNA3NMwS32OwYS2TtMo'\
        + 'SxuRKUwXYo6zFSG7g3tsu-22KAYh1aZxFJGUyyaaY_4BqzzCJrn7nTHxIZime0ZQ9GHu1Um_'\
        + 'NWCsfAgddixEcvN82Qi_N6ckwiZZt-n997cZxrX3I7-yPyNNeO7E'\
        + 'X4LV3D8JL56DfCPW7TEI-jaL1kFgIcgv28J0CuN_bsUaMCG3uD8zYF03YhT86s1-dznZuani'\
        + 'jgp97fOs9__Gd4Iq3aaEc8RlHU6uyi3KDP-XKyJtdcS0VKisohcM'\
        + 'rztKYt3SbMLYq9XQlFLn-6Tb7OnJ-kDdiyyxA440bcBBEQAKGA'

        # ### Нужно еще на забыть указать здесь папку
        head = {'Authorization': f'Bearer {token}'}
        response = urllib3.PoolManager().request("GET", url=item_href, headers=head)
        if response.status == 200:
            gdal_rast_handler(response.data, datetime='123')
            response.close()
            return f'Complete'
        else: 
            response.close()
            return f'Cant connect to this uri'
        
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

def gdal_rast_handler(*args: str, datetime: str) -> GDALRaster:
    """
    Создает .tif файл из виртуальных .tif файлов
    
    Или может создать один .tif с несколькими каналами из нескольких .tif с одним каналом

    Args:
        *args (str):
            Принмает в себя ссылки на .tif файл.
        datetime (str):
            Задает имя снимку исходя из даты его создания
    Returns:
        Image (byte or .tif):
            Возвращает созданный/объединенный .tif новым файлов
            и в течении сессии сохраняется в оперативной памяти.
    """
    img_list_handler = []
    for value in args:
        value = GDALRaster(value)
        img_list_handler.append(value)

    source = img_list_handler[0]
    source_driver = source.driver

    # в name указывается имя директории, в которую сохранится файл
    raster_create = GDALRaster(
        {
            'srid': source.srid,
            'width': source.width,
            'height': source.height,
            'driver': str(source_driver),
            'name': f'IMAGES/{str(datetime)}.tif',
            'datatype': source.bands[0].datatype(),
            'nr_of_bands': len(img_list_handler),
        }
    )

    for y in range(len(img_list_handler)):
        raster_create.bands[y].data(img_list_handler[y].bands[0].data())
    
    return raster_create

def delete_image(polygon):
    ImageInstance = Image.objects.get(polygon=polygon)
    remove(str(ImageInstance.url))
    ImageInstance.delete()

def update_image_GEE(polygon):
    delete_image(polygon)
    new_image = Image_From_GEE(polygon)
    new_image.download_image()
    new_image.visualization()