
# УРЛЫ ПРИЛОЖУХИ

from django.urls import path
from . import views

urlpatterns = [
    path('', views.MapView.as_view(), name='map'),
    path('sign-in/', views.RegistrationView.as_view(), name='sign-in'),
    path('log-in/', views.LoginView.as_view(), name='log-in'),
    path('log-out/', views.logoutView, name='log-out'),
    path('create-polygon/', views.CreatePolygon.as_view(), name='create-polygon'),
    path('get-polygons/', views.GetPolygons.as_view(), name='get-polygon'),
    path('delete-polygon/', views.DeletePolygon.as_view(), name='delete-polygon'),
    path('update-polygon/', views.UpdatePolygon.as_view(), name='update-poligon'),
    path('upload-img/', views.UploadImg.as_view(), name='upload-img')
]
