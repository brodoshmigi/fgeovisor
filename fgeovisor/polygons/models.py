from uuid import uuid4

from django.contrib.gis.db import models
from django.contrib.auth.models import User

# 24.02.2025
# SELECT pg_size_pretty( pg_relation_size( 'table' ) );


class Bounds(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    code = models.IntegerField()
    name = models.CharField(max_length=35)
    geom = models.GeometryField(srid=4326)

    def __str__(self):
        return f"{self.name}"
    
    class Meta:
        ordering = ["name"]


class Polygons(models.Model):
    """ Абстрактная модель полигона """
    polygon_id = models.UUIDField(primary_key=True,
                                  default=uuid4,
                                  editable=False)
    polygon_data = models.PolygonField(srid=4326)

    # need index
    district = models.ForeignKey(Bounds,
                                 verbose_name=("district"),
                                 on_delete=models.CASCADE)

    class Meta:
        # unique_together = ['owner', 'polygon_data', 'polygon_id']
        abstract = True


class UserPolygon(Polygons):
    """ 
    fields:
    - polygond_id
    - polygon_data
    - district
    - owner
    select by 2 fields
    """
    owner = models.ForeignKey(User,
                              related_name=("polygons"),
                              verbose_name=("created by"),
                              on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Полигон - {self.owner}, создан - {self.created_at} в {self.district}"


class ImageBounds(Polygons):
    """
    fields:
    - polygon_id
    - polygon_data
    - disctrict 
    """

    class Meta:
        ordering = ["polygon_data"]
