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

def delete_image(polygon):
    ImageInstance = Image.objects.get(polygon=polygon)
    remove(str(ImageInstance.url))
    ImageInstance.delete()

def update_image_GEE(polygon):
    delete_image(polygon)
    new_image = Image_From_GEE(polygon)
    new_image.download_image()
    new_image.visualization()
