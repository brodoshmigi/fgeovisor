import ee 
import datetime
import requests
from os import (makedirs, remove, path, listdir)
from django.contrib.gis.gdal.raster.source import GDALRaster
from zipfile import ZipFile
from numpy import seterr, nanmax
from .models import Image
from matplotlib.pyplot import(imshow, imsave)
from polygons.serializators import PolygonFromDbSerializer

#ee.Authenticate()
ee.Initialize(project='ee-cocafin1595')
IMAGE_DIR = path.dirname(path.abspath(__file__)) + '/IMAGES'


class Image_From_GEE():
    
    def __init__(self, polygon, dir=IMAGE_DIR + '/' + 'image' + str(len(listdir(IMAGE_DIR)) + 1),
                  date_start='2023-01-01', date_end=str(datetime.date.today())):
        print(listdir(IMAGE_DIR))
        self.polygon = polygon
        self.coords = ee.Geometry.Polygon(PolygonFromDbSerializer(polygon).data['geometry']['coordinates'])
        self.dir = dir
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
        valid_array = imshow(ndvi).get_array()
        imsave((self.dir + '/' + 'ndvi.png'), valid_array)
        image_DB = Image(polygon=self.polygon, url=(self.dir + '/' + 'ndvi.png'))
        image_DB.save()