from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer

from .models import UserPolygon, ImageBounds

# Получает queryset из модели Polygon
class PolygonSerializator(serializers.ModelSerializer):

    class Meta:
        model = UserPolygon
        fields = '__all__'

class GeoJSONSerializer(GeoFeatureModelSerializer):
     
    class Meta:
        model = UserPolygon
        fields = ['polygon_id','polygon_data']
        geo_field = 'polygon_data'