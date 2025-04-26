from abc import abstractmethod

from django.db import models

from polygons.models import UserPolygon, ImageBounds
""" check() к сожалению нарушает DRY ((( из-за этого никто не апнет предатора в апексе """
# 24.02.2025


class Image(models.Model):
    """ Абстрактная модель изображения """

    _next_handler: models.Model = None

    local_uri = models.ImageField(blank=True)
    cloud_uri = models.URLField(blank=True)
    image_date = models.DateField()

    def set_next(self, h: models.Model) -> models.Model:
        self._next_handler = h
        return h

    @abstractmethod
    def check_uri(self, request):
        if self._next_handler:
            return self._next_handler.check()

        return None

    class Meta:
        abstract = True

class ImageHandler(models.Model):

    def check_uri(self, request = None):
        pass


    class Meta:
        abstract = True

class ImageType(models.Model):
    """ Абстрактный миксин для добавления коэффициентов """

    # len = 6
    enum_index = {
        "NDVI": "ndvi",     # Вегетационный индекс растительности
        "EVI": "evi",       # Улучшенный индекс растительности
        "SAVI": "savi",     # Индекс растительности с поправкой на почву
        "GNDVI": "gndvi",   # NDVI только с зеленым каналом
        "MSAVI": "msavi",   # Модификация savi
        "NDRE": "ndre"      # Нормализованный индекс красного края (хз что это)
    }
    image_index = models.CharField(max_length=5,
                                   choices=enum_index,
                                   default="NDVI")

    class Meta:
        abstract = True


class NasaImage(Image):
    """ Example for NASA cloud-schema image (usually json) """
    polygon_bounds = models.ForeignKey(to=ImageBounds,
                                       to_field="polygon_id",
                                       related_name=("nasa_image"),
                                       on_delete=models.CASCADE)
    local_uri = models.JSONField(null=True)

    def check_uri(self, request) -> str:
        if self.cloud_uri:
            return self.cloud_uri

        if self.local_uri:
            return self.local_uri

        return super().check_uri(request)

    class Meta:
        ordering = ["image_date"]


class UserImage(Image, ImageType):
    """ 
    fields:
    - polygon_id
    - local_uri
    - cloud_uri
    - image_date
    - image_index
    """
    polygon_id = models.ForeignKey(to=UserPolygon,
                                   to_field="polygon_id",
                                   related_name=("user_image"),
                                   on_delete=models.CASCADE)

    def check_uri(self, request) -> str:

        if self.cloud_uri:
            return self.cloud_uri

        if self.local_uri:
            return self.local_uri.url

        return super().check_uri(request)
    
    def __str__(self):
        return f"{self.image_index} - {self.image_date}"

    class Meta:
        ordering = ["polygon_id"]
