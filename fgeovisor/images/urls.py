from django.urls import path

from . import views

# query-params: ?id=id&date=date&index=index
urlpatterns = [
    path('get-img', views.UploadImg.as_view(), name='get-img'),
    path('get-img-gee', views.ImageGEE.as_view(), name='get-img')
]