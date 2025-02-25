import uuid

from django.contrib.gis.db import models
from django.contrib.auth.models import User

# 24.02.2025
# SELECT pg_size_pretty( pg_relation_size( 'table' ) );

class Polygons(models.Model):
    """ Абстрактная модель полигона """
    polygon_id = models.UUIDField(primary_key=True,
                                  default=uuid.uuid4,
                                  editable=False)
    polygon_data = models.PolygonField()

    class Meta:
        # unique_together = ['owner', 'polygon_data', 'polygon_id']
        abstract = True


class UserPolygon(Polygons):
    """ Модель полигонов, которые создаются пользователями """
    owner = models.ForeignKey(User,
                              related_name=('polygons'),
                              verbose_name=("created by"),
                              on_delete=models.CASCADE)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Полигон - {self.owner}, создан - {self.created_at}"

class ImageBounds(Polygons):
    """ Границы снимка наса """
    class Meta:
        ordering = ['polygon_data']