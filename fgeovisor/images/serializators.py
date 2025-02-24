from rest_framework import serializers

from .models import UserImage, NasaImage

class ImageSerializator(serializers.ModelSerializer):

    class Meta:
        model = UserImage
        fields = ['id', 'url']