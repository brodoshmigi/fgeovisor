import ee 
import datetime
import requests
import time
import pystac_client
import pystac as stac
from functools import lru_cache
from pystac_client.client import Client
from os import (makedirs, remove, path, listdir)
from django.contrib.gis.gdal.raster.source import GDALRaster
from zipfile import ZipFile
from numpy import seterr, nanmax
from .models import Image
from matplotlib.pyplot import(imshow, imsave)
from matplotlib import use
from polygons.serializators import PolygonFromDbSerializer


ee.Authenticate()
ee.Initialize(project='ee-nezhentsev2017')
IMAGE_DIR = path.dirname(path.abspath(__file__)) + '/IMAGES'


class Image_From_GEE():
    
    def __init__(self, polygon,
                  date_start='2023-01-01', date_end=str(datetime.date.today())):
        self.polygon = polygon
        self.coords = ee.Geometry.Polygon(PolygonFromDbSerializer(polygon).data['geometry']['coordinates'])
        self.dir = IMAGE_DIR + ('/image' + str(len(listdir(IMAGE_DIR)) + 1))
        self.date_start = date_start
        self.date_end = date_end
        print(listdir(IMAGE_DIR))
        print(self.dir)
    
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
        imsave((self.dir + '/' + 'ndvi.png'), valid_array)
        image_DB = Image(polygon=self.polygon, url=(self.dir + '/' + 'ndvi.png'))
        image_DB.save()


class ImageFromCMRStac:
    def __init__(self, href = 'https://cmr.earthdata.nasa.gov/stac', 
                 satelite_names: (str | list) = 'landsat', bbox: float = None, 
                 datetime: str = None, catalog_list: list = None, 
                 DIR_NAME: str = None, headers: dict = None):
        """
        Класс поиска и загрузи .tif файлов из CMR NASA

        ## ARGS
        ### href 
        RU: Ссылка на ***Родительский*** **стак** файл(каталог), может быть как **http(s)://** так и **C:/**
        - пример: https://cmr.earthdata.nasa.gov/stac

        EN: link to ***ROOT*** **stac** file(catalog), it can be: **http(s)://** or **C:/**
        - example: https://cmr.earthdata.nasa.gov/stac
        ### satelite_name
        RU: ищет по имени спутника
        - пример: landsat, hlsl, sentinel, hlss

        EN: filtering by given satelite name, it can be lowercase
        - example: landsat, hlsl, sentinel, hlss
        ### bbox
        RU: Указывает зону интереса
        - обычно список или кортеж, но желательно GEOJSON

        EN: it presents interesting for you zone to filter images
        - welcome list or tuple, but pref GEOJSON;
        ### datetime
        RU: указывает время для поиска по нему

        EN: it presents interesting for you datetime to filter images
        ### catalog_list
        RU: список организаций для поиска по ним

        EN: it presents list of org names, who used for filter collections
        ### DIR_NAME
        RU: для сохранения имаге

        EN: needs to save images 
        """
        self.href = stac.Link('root', href)
        self.satelite_name = satelite_names
        self.bbox = bbox
        self.datetime = datetime
        self.catalog_list = catalog_list
        self.DIR_NAME = DIR_NAME
        # Создаем экземпляр pystac.Catalog
        self.stack_obj = self.href.resolve_stac_object()
        self.root_catalog = stac.Catalog.from_file(self.stack_obj)
        self.catalog_links = []

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
       return [link.get_href() for link in self.get_childs() if link.title in self.catalog_list]
            
    # это хренота пока не работает, но думаю если setter добавить оно пойдет
    def _get_satelite_name(self):
        if type(self.satelite_name) == type([]):
            return self.satelite_name[0]
        else:
            return self.satelite_name

    def search_org_catalogs(self):
        true_collections = []
        SEARCH_LIST = set([id.lower() for id in self.satelite_name])
        for link in self._get_childs():
            collections_client = self._open_client(link)
            search_collections = collections_client\
                .collection_search(q='landsat',
                                   bbox=self.bbox,
                                   datetime=self.datetime)
            true_collections.extend(
                collection.id for collection in search_collections.collections()
                if any(id in collection.id.lower() for id in SEARCH_LIST)
            )
        return true_collections
            
    def get_items(self):
        true_collections = self.search_org_catalogs()
        for link in self._get_childs():
            items = self._open_client(link)
            item_search = items.search(
                collections=true_collections,
                bbox=self.bbox,
                datetime=self.datetime)
            for item in item_search.items():
                yield item.id