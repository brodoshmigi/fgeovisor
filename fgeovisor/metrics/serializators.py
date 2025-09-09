from rest_framework import serializers

from .models import Metrics

class ImageSerializator(serializers.ModelSerializer):

    class Meta:
        model = Metrics
        fields = "__all__"