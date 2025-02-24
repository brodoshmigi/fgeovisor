from django.urls import path

from . import views

urlpatterns = [
    path('create-polygon/', views.CreatePolygon.as_view(), name='create-polygon'),
    path('get-polygons/', views.GetPolygons.as_view(), name='get-polygon'),
    path('delete-polygon/', views.DeletePolygon.as_view(), name='delete-polygon'),
    path('update-polygon/', views.UpdatePolygon.as_view(), name='update-poligon')
]
