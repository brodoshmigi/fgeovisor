import ee
import requests
import logging
from datetime import date
from os import (makedirs, remove, listdir, rmdir, name)
from zipfile import ZipFile
from matplotlib.pyplot import imsave

from django.contrib.gis.gdal.raster.source import GDALRaster

from polygons.serializators import GeoJSONSerializer
from polygons.models import UserPolygon

from images.models import UserImage
from staff.core.index_calculations import (calculate_NDVI, calculate_EVI,
                                           calculate_SAVI, calculate_GNDVI,
                                           calculate_MSAVI, calculate_NDRE,
                                           crop_image)

logger = logging.getLogger(__name__)

IMAGE_DIR = "images/IMAGES"

RATIO_ENUM_S2_BANDS = {
    "NDVI": ["B4", "B8"],  # Вегетационный индекс растительности
    "EVI": ["B4", "B8", "B2"],  # Улучшенный индекс растительности
    "SAVI": ["B4", "B8"],  # Индекс растительности с поправкой на почву
    "GNDVI": ["B3", "B8"],  # NDVI только с зеленым каналом
    "MSAVI": ["B4", "B8"],  # Модификация savi
    "NDRE": ["B6", "B8"]  # Нормализованный индекс красного края (хз что это)
}

RATIO_ENUM_LANDSAT_BANDS = {
    "NDVI": [],
    "EVI": [],
    "SAVI": [],
    "GNDVI": [],
    "MSAVI": [],
    "NDRE": []
}

RATIO_ENUM_CALLBACK = {
    "NDVI": calculate_NDVI,
    "EVI": calculate_EVI,
    "SAVI": calculate_SAVI,
    "GNDVI": calculate_GNDVI,
    "MSAVI": calculate_MSAVI,
    "NDRE": calculate_NDRE
}

INDEX_EXPRESSION = {
    # B8 - NIR
    # B4 - RED
    # B2 - BLUE
    # B3 - GREEN
    # B6 - EDGE RED
    "NDVI": "(b(8) - b(4)) / (b(8) + b(4))",
    "EVI": "2 * (b(8) - b(4)) / (b(8) + 6*b(4) - 7.5*b(2) + 1)",
    "SAVI": "1.5 * ((b(8) - b(4)) / (b(8) + b(4) + 0.5))",
    "GNDVI": "(b(8) - b(3)) / (b(8) + b(3))",
    "MSAVI":
    "(2 * b(8) + 1 - sqrt((2 * b(8) + 1)*(2 * b(8) + 1) - 8 * (b(8) - b(4)))) / 2",
    "NDRE": "(b(8) - b(6)) / (b(8) + b(6))"
}


class GoogleDataLoader():

    def __init__(self,
                 polygon: UserPolygon,
                 index: str = "NDVI",
                 date_start: str = "2023-01-01",
                 date_end: str = str(date.today())):

        self.polygon_object = polygon
        self.index = index
        self.dir = (IMAGE_DIR +
                    f"/{self.polygon_object.polygon_id}_{index}_{date_start}")
        self.date_start = date_start
        self.date_end = date_end
        self.REDUCER = (ee.Reducer.min().combine(ee.Reducer.max(),
                                                 sharedInputs=True).combine(
                                                     ee.Reducer.mean(),
                                                     sharedInputs=True))

    # 40 < 50
    def load_data_reducer(self):
        """ reducer значит в облаке """

        polygon_ee_obj = ee.Geometry.Polygon(
            GeoJSONSerializer(
                self.polygon_object).data["geometry"]["coordinates"])

        collection = (
            ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED").filterDate(
                self.date_start,
                self.date_end).filterBounds(polygon_ee_obj).filter(
                    ee.Filter.lt("CLOUD_COVERAGE_ASSESSMENT", 10)))

        # logger.debug("%s", collection.first().bandNames().getInfo())
        # logger.debug("%s", collection.size().getInfo())

        if collection.size().getInfo() == 0:
            return []

        def compute_bands(img):
            """ compute значит в облаке, кампот"""
            for name, formula in INDEX_EXPRESSION.items():
                img = img.addBands(img.expression(formula).rename(name))
            return img

        collection = collection.map(compute_bands)

        def compute_stats(img):
            """ камшот значит в облаке """
            img = img.select([*INDEX_EXPRESSION.keys()])
            result = img.reduceRegion(reducer=self.REDUCER,
                                      geometry=polygon_ee_obj,
                                      scale=10,
                                      bestEffort=True)
            return ee.Feature(
                None, result.set("date",
                                 img.date().format("YYYY-MM-dd")))

        result = collection.map(compute_stats).getInfo()["features"]

        # logger.debug("%s", result.getInfo()["features"])

        # logger.debug("%s", result_list)
        result_list = [f["properties"] for f in result]

        return result_list

    def get_download_url(self) -> str:
        polygon_EE = ee.Geometry.Polygon(
            GeoJSONSerializer(
                self.polygon_object).data["geometry"]["coordinates"])
        sentinel_image = ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED") \
            .filterDate(self.date_start, self.date_end) \
            .filterBounds(polygon_EE) \
            .filter(ee.Filter.lt("CLOUD_COVERAGE_ASSESSMENT", 10)) \
            .select(RATIO_ENUM_S2_BANDS[self.index]) \
            .first() \
            .reproject(crs="EPSG:4326", scale=10) \
            .clip(polygon_EE)
        return sentinel_image.getDownloadURL()

    def download_image(self):
        response = requests.get(self.get_download_url())
        path = self.dir + ".zip"
        with open(path, "wb") as fd:
            fd.write(response.content)
        extract_to_directory = path.replace(".zip", "")
        makedirs(extract_to_directory)
        with ZipFile(path, "r") as zip_ref:
            zip_ref.extractall(extract_to_directory)
        remove(path)

    def read_bands(self) -> list[GDALRaster]:
        list_of_rasters = listdir(self.dir)
        bands = [
            GDALRaster(self.dir + "/" + item).bands[0].data().astype("float64")
            for item in list_of_rasters
        ]
        return bands

    def remove_bands(self):
        list_of_rasters = listdir(self.dir)
        [remove(self.dir + "/" + item) for item in list_of_rasters]
        rmdir(self.dir)

    def calculate_index(self):
        index = RATIO_ENUM_CALLBACK[self.index](*self.read_bands())
        url_raster = self.dir + "/" + str(listdir(self.dir)[0])
        polygon = GeoJSONSerializer(self.polygon_object).data["geometry"]
        valid_array = crop_image(url_raster, polygon, index)
        imsave((self.dir + ".png"), valid_array, vmin=-1, vmax=1)
        image_DB = UserImage(polygon_id=self.polygon_object,
                             image_index=self.index,
                             local_uri=(self.dir + ".png"),
                             image_date=self.date_start)
        image_DB.save()
        return image_DB

    def auth(self):
        if name == "posix":
            credentials = ee.ServiceAccountCredentials("", "./service.json")
            ee.Initialize(credentials=credentials)
        else:
            ee.Authenticate()
            ee.Initialize(project="ee-cocafin1595")
