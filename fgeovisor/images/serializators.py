from rest_framework import serializers
from .models import Image

class ImageSerializator(serializers.ModelSerializer):

    class Meta:
        model = Image
        fields = ['id', 'url']