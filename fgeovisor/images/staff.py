import ee
import requests
from datetime import date
from os import (makedirs, remove, path, listdir, rmdir)
from zipfile import ZipFile
from numpy import seterr
from matplotlib.pyplot import (imshow, imsave)

from django.contrib.gis.gdal.raster.source import GDALRaster

from .models import UserImage
from polygons.serializators import GeoJSONSerializer
from polygons.models import UserPolygon


def delete_image(polygon):
    ImageInstances = UserImage.objects.filter(polygon=polygon)
    for ImageInstance in ImageInstances:
        remove(str(ImageInstance.local_uri))
        ImageInstance.delete()

def update_image_GEE(polygon):
    delete_image(polygon)
    new_image = Image_GEE(polygon)
    new_image.download_image()
    new_image.visualization()

def calculate_NDVI(image_url:str):
    list_of_rasters = listdir(image_url)
    red = GDALRaster(image_url + '/' + list_of_rasters[0]).bands[0].data()
    nir = GDALRaster(image_url + '/' + list_of_rasters[1]).bands[0].data()
    seterr(divide='ignore', invalid='ignore')
    ndvi = (nir - red) / (nir + red)
    return ndvi

def calculate_EVI(image_url:str):
    list_of_rasters = listdir(image_url)
    red = GDALRaster(image_url + '/' + list_of_rasters[0]).bands[0].data()
    nir = GDALRaster(image_url + '/' + list_of_rasters[1]).bands[0].data()
    Blue = GDALRaster(image_url + '/' + list_of_rasters[2]).bands[0].data()
    
def calculate_SAVI(image_url:str, L:float= 0.5):
    list_of_rasters = listdir(image_url)
    red = GDALRaster(image_url + '/' + list_of_rasters[0]).bands[0].data()
    nir = GDALRaster(image_url + '/' + list_of_rasters[1]).bands[0].data()
    
def calculate_GNDVI(image_url:str):
    list_of_rasters = listdir(image_url)
    green = GDALRaster(image_url + '/' + list_of_rasters[0]).bands[0].data()
    nir = GDALRaster(image_url + '/' + list_of_rasters[1]).bands[0].data()

def calculate_MSAVI(image_url:str, L:float= 0.5):
    list_of_rasters = listdir(image_url)
    red = GDALRaster(image_url + '/' + list_of_rasters[0]).bands[0].data()
    nir = GDALRaster(image_url + '/' + list_of_rasters[1]).bands[0].data()

def calculate_NDRE(image_url:str, L:float= 0.5):
    list_of_rasters = listdir(image_url)
    red_edge = GDALRaster(image_url + '/' + list_of_rasters[0]).bands[0].data()
    nir = GDALRaster(image_url + '/' + list_of_rasters[1]).bands[0].data()


IMAGE_DIR = path.dirname(path.abspath(__file__)) + '/IMAGES'

RATIO_ENUM_S2_BANDS = {
        'NDVI': ['B4', 'B8'],            # Вегетационный индекс растительности
        'EVI': ['B4', 'B8', 'B2'],       # Улучшенный индекс растительности
        'SAVI': ['B4', 'B8'],            # Индекс растительности с поправкой на почву
        'GNDVI': ['B3', 'B8'],           # NDVI только с зеленым каналом
        'MSAVI': ['B4', 'B8'],           # Модификация savi
        'NDRE': ['B6', 'B8']             # Нормализованный индекс красного края (хз что это)
        }

RATIO_ENUM_LANDSAT_BANDS = {
        'NDVI': [],    
        'EVI': [],     
        'SAVI': [],    
        'GNDVI': [],   
        'MSAVI': [],   
        'NDRE': []     
        }

RATIO_ENUM_CALLBACK = {
        'NDVI': calculate_NDVI,     
        'EVI': calculate_EVI,       
        'SAVI': calculate_SAVI,     
        'GNDVI': calculate_GNDVI,   
        'MSAVI': calculate_MSAVI,   
        'NDRE': calculate_NDRE      
        }

class Image_GEE():

    def __init__(self,
                 polygon : UserPolygon,
                 index : str ='NDVI',
                 date_start : str ='2023-01-01',
                 date_end : str =str(date.today())):
        self.polygon = polygon
        self.index = index.upper()
        self.coords = ee.Geometry.Polygon(
            GeoJSONSerializer(polygon).data['geometry']['coordinates'])
        self.dir = IMAGE_DIR + (f'/{index}' + str(len(listdir(IMAGE_DIR)) + 1))
        self.date_start = date_start
        self.date_end = date_end

    def get_download_url(self) -> str:
        sentinel_image = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED') \
            .filterDate(self.date_start, self.date_end) \
            .filterBounds(self.coords) \
            .filter(ee.Filter.lt('CLOUD_COVERAGE_ASSESSMENT', 10)) \
            .select(RATIO_ENUM_S2_BANDS[self.index]) \
            .first() \
            .reproject(crs='EPSG:3857', scale=5) \
            .clip(self.coords)
        return sentinel_image.getDownloadURL()

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

    def calculate_index(self):
        index = RATIO_ENUM_CALLBACK[self.index](self.dir)
        valid_array = imshow(index).get_array()
        imsave((self.dir + '.png'), valid_array, vmin=0, vmax=1)
        image_DB = UserImage(polygon_id=self.polygon,
                         local_uri=(self.dir + '.png'),
                         image_date=self.date_start)
        image_DB.save()
        remove(self.dir + '/' + listdir(self.dir)[0])
        remove(self.dir + '/' + listdir(self.dir)[0])
        rmdir(self.dir)
        return image_DB

    '''
    def visualization(self):
        list_of_rasters = listdir(self.dir)
        red = GDALRaster(self.dir + '/' + list_of_rasters[0]).bands[0].data()
        nir = GDALRaster(self.dir + '/' + list_of_rasters[1]).bands[0].data()
        seterr(divide='ignore', invalid='ignore')
        ndvi = (nir - red) / (nir + red)
        valid_array = imshow(ndvi).get_array()
        imsave((self.dir + '.png'), valid_array, vmin=0, vmax=1)
        image_DB = UserImage(polygon=self.polygon,
                         url=(self.dir + '.png'),
                         date=self.date_start)
        image_DB.save()
        remove(self.dir + '/' + listdir(self.dir)[0])
        remove(self.dir + '/' + listdir(self.dir)[0])
        rmdir(self.dir)
    '''

ee.Authenticate()
ee.Initialize(project='ee-cocafin1595')