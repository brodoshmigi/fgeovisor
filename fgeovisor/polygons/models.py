import uuid
from django.contrib.gis.db import models
from django.contrib.auth.models import User

# Модель полигона
class Polygon(models.Model):
    polygon_id = models.UUIDField(primary_key=True, default=uuid.uuid4, 
                                    editable=False)
    polygon_data = models.PolygonField()
    owner = models.ForeignKey(User, related_name=('polygons'), 
                                verbose_name=("created by"), 
                                  on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['owner', 'polygon_data', 'polygon_id']

    def __str__(self):
        return f"Полигон - {self.owner}, создан - {self.created_at}"