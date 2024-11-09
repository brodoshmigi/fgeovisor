from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from .models import Polygon

# Получает queryset из модели Polygon
class PolygonSerializator(serializers.ModelSerializer):

    class Meta:
        model = Polygon
        fields = '__all__'

class PolygonFromDbSerializer(GeoFeatureModelSerializer):
     
    class Meta:
        model = Polygon
        fields = ['polygon_id','polygon_data']
        geo_field = 'polygon_data'