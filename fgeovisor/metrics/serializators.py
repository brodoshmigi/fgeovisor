from rest_framework import serializers

from .models import Metrics

class MetricSerializator(serializers.ModelSerializer):

    class Meta:
        model = Metrics
        fields = ["storage", "date"]