from django.urls import path

from .views import (MetricsViewSet)

urlpatterns = [
    path('metrics',
         MetricsViewSet.as_view({'get': 'list'}),
         name='get-metrics'),
]