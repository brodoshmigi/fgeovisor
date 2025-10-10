from django.db import models

from polygons.models import UserPolygon

class Metrics(models.Model):

    polygon_id = models.ForeignKey(UserPolygon,
                                   to_field="polygon_id",
                                   verbose_name="Принадлежит ",
                                   on_delete=models.CASCADE)

    storage = models.JSONField()
    date = models.DateField()

    def __str__(self):
        return f"{self.date} - {self.polygon_id}"