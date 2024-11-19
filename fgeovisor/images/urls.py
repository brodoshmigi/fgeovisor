from django.urls import path
from . import views

urlpatterns = [
    path('get-img/<id>', views.UploadImg.as_view(), name='get-img')
]