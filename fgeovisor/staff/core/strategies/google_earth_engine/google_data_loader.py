import ee
import requests
import logging
from datetime import date
from os import (makedirs, remove, name)
from zipfile import ZipFile
from matplotlib.pyplot import imsave
from typing import List, Any

from polygons.serializators import GeoJSONSerializer
from polygons.models import UserPolygon

from visor_bend_site.settings import MEDIA_ROOT, GOOGLE_PROJ_NAME

from images.models import UserImage
from staff.core.gdal_calculations import (calculate_NDVI, calculate_EVI,
                                          calculate_SAVI, calculate_GNDVI,
                                          calculate_MSAVI, calculate_NDRE,
                                          crop_image, read_bands, remove_bands)
from staff.interfaces.strategies.loader import DataLoader

logger = logging.getLogger(__name__)


# Все расчеты индексов нужно по хорошему делить на 10000 тысяч, это просто так, заметка
# Nasa mentioned

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


class GoogleDataLoader(DataLoader):

    def __init__(self,
                 polygon: UserPolygon,
                 index: str = "NDVI",
                 date_start: str = "2023-01-01",
                 date_end: str = str(date.today())):

        self.polygon_object = polygon
        self.index = index
        self.dir = (MEDIA_ROOT /
                    f"{self.polygon_object.polygon_id}_{index}_{date_start}")
        self.date_start = date_start
        self.date_end = date_end
        self.REDUCER = (ee.Reducer.min().combine(ee.Reducer.max(),
                                                 sharedInputs=True).combine(
                                                     ee.Reducer.mean(),
                                                     sharedInputs=True))

    def auth(self) -> None:
        if name == "posix":
            credentials = ee.ServiceAccountCredentials("", "./service.json")
            ee.Initialize(credentials=credentials)
        else:
            ee.Authenticate()
            ee.Initialize(project=GOOGLE_PROJ_NAME)

    def _get_sentinel_collection(self, ee_poly_obj):
        return (ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
                .filterDate(self.date_start, self.date_end)
                .filterBounds(ee_poly_obj)
                .filter(ee.Filter.lt("CLOUD_COVERAGE_ASSESSMENT", 10)))

    def _get_download_url(self) -> str:
        """
        Задание от Тайлера: Сделать маскировку облачности по пикселям(метод QA60 - Quality Assurance),
        вместо ee.Filter.lt
        """
        ee_poly_obj = ee.Geometry.Polygon(
            GeoJSONSerializer(
                self.polygon_object).data["geometry"]["coordinates"])

        sentinel_image = (self._get_sentinel_collection(ee_poly_obj)
                          .select(RATIO_ENUM_S2_BANDS[self.index])
                          .first()
                          .reproject(crs="EPSG:4326", scale=10)
                          .clip(ee_poly_obj))

        return sentinel_image.getDownloadURL()

    # 36 < 50
    def load_data(self) -> List[Any]:
        """ облачная функция """

        ee_poly_obj = ee.Geometry.Polygon(
            GeoJSONSerializer(
                self.polygon_object).data["geometry"]["coordinates"])

        collection = self._get_sentinel_collection(ee_poly_obj)

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
                                      geometry=ee_poly_obj,
                                      scale=10,
                                      bestEffort=True)
            return ee.Feature(
                None, result.set("date",
                                 img.date().format("YYYY-MM-dd")))
        # Убийца синхронных очередей
        result = collection.map(compute_stats).getInfo()["features"]

        # logger.debug("%s", result.getInfo()["features"])

        # logger.debug("%s", result_list)
        result_list = [f["properties"] for f in result]

        return result_list

    def download_image(self) -> None:
        """
        Задание от Тайлера: читать изображение напрямую,
        например, через io.BytesIO. Нахуя? Потому что,
        изображение и так нихуя не весит из гугла, так что,
        это оптимизация. Если сосал - можно не делать.
        """
        response = requests.get(self._get_download_url())
        exctract_path = self.dir.with_suffix(".zip")

        with open(exctract_path, "wb") as fd:
            fd.write(response.content)

        makedirs(self.dir)

        with ZipFile(exctract_path, "r") as zip_ref:
            zip_ref.extractall(self.dir)

        remove(exctract_path)

    def calculate_index(self) -> UserImage:
        # Возможно как input параметр нужно будет конвертировать в str
        raster_path = self.dir / next(self.dir.iterdir())
        output_path = self.dir.with_suffix(".png")

        index = RATIO_ENUM_CALLBACK[self.index](*read_bands(self.dir))
        polygon = GeoJSONSerializer(self.polygon_object).data["geometry"]

        valid_array = crop_image(raster_path, polygon, index)
        imsave(output_path, valid_array, vmin=-1, vmax=1)

        image_DB = UserImage(polygon_id=self.polygon_object,
                             image_index=self.index,
                             local_uri=output_path,
                             image_date=self.date_start)
        image_DB.save()

        remove_bands(self.dir)
        return image_DB
