# Тестовый файл для функций, вычисляющих метрики
# Нужен, чтобы тестировать их, перед внедрением с
# помощью Celery и Redis.

import pandas as pd
import logging
from json import dumps

from django.contrib.gis.geos import Polygon

from staff.core.context.loader_context import CalculationContext

from polygons.models import UserPolygon
from images.models import UserImage

from metrics.models import Metrics

logger = logging.getLogger(__name__)

COLUMNS_ORDER = [
    "EVI_max", "EVI_min", "EVI_mean",
    "NDVI_max", "NDVI_min", "NDVI_mean",
    "NDRE_max", "NDRE_min", "NDRE_mean",
    "SAVI_max", "SAVI_min", "SAVI_mean",
    "GNDVI_max", "GNDVI_min", "GNDVI_mean",
    "MSAVI_max", "MSAVI_min", "MSAVI_mean"
]

def calculate_default_polygon_stats(obj: UserPolygon, date: str):

    obj_data: Polygon = obj.polygon_data

    num_coords = obj_data.num_coords
    area = obj_data.area

    stats = Metrics.objects.create(polygon_id=obj,
                                   storage={
                                       "Кол-во точек": num_coords,
                                       "Площадь": area
                                   },
                                   date=date)
    stats.save()

    return stats


def compute_index_stats_range(context: CalculationContext, obj: UserPolygon,
                              start: str, end: str):
    """ compute это значит в облаке """

    # obj_data: Polygon = obj.polygon_data

    collection = context.metrics(obj, date_start=start, date_end=end)
    # logger.debug("%s", collection)

    df = pd.DataFrame(collection)
    df["date"] = pd.to_datetime(df["date"])
    df.set_index("date", inplace=True)
    df.sort_values("date", ascending=False, inplace=True)

    # logger.debug("%s", df)
    metrics_list = [
        Metrics(
            polygon_id=obj,
            storage=row.to_dict(),
            date=index
        ) for index, row in df.iterrows()
    ]

    Metrics.objects.bulk_create(metrics_list)

    return Metrics.objects.all()


def local_index_stats_range(obj: UserPolygon, start: str, end: str):
    """ Единственное решение данной проблемы - свое хранилище снимков
        Естественно на определенной территории. Иначе, это будет ужасно
        плохо и больно.
    """
    return NotImplementedError(
        """ Данная хрень получится, только если делать это во время скачивания снимков
        То есть мы распаралеливаем действия, одна ветка будет скачивать, другая же
        будет вычислять метрики, после того, как снимок скачался, но это черевато
        потерями времени, так как, один снимок скачивается 2 сек минимально, то мы
        получать метрики будем только спустя 2 секунды на каждый индекс, а значит,
        к выводу статистики по последнему индексу пройдет +- 10 секунд) Однако, раз
        мы расспаралеливаем действия, то начало операции скачивания начнется раньше,
        чем пользователь зайдет на полигон, то есть при создании мы будем получать эти
        данные, тогда все данные для пользователя будут скачиваться +- 5 секунд. Но,
        это тоже плохо, так как если пользователь сразу захочет удалить полигон, то для
        нас это будет потеря ресурса и времени вычисления, крч, ну за ящиком """
    )
