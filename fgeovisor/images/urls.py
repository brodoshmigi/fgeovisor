from django.urls import path

from . import views

urlpatterns = [
    path('get-img/<id>/<date>', views.UploadImg.as_view(), name='get-img'),
    path('get-img-gee/<id>/<date>', views.ImageGEE.as_view(), name='get-img')
]