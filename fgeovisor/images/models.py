from django.db import models
from polygons.models import Polygon

# Модель изображения
class Image(models.Model):
    polygon = models.ForeignKey(Polygon, related_name=('images'), 
                                    on_delete=models.CASCADE)
    # Ссылка на изображение или путь в хранилище
    url = models.ImageField(upload_to='fgeovisor/web_interface/IMAGES')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
