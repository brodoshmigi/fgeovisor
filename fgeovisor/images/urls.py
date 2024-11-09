from django.urls import path
from . import views

urlpatterns = [
    path('upload-img/', views.UploadImg.as_view(), name='upload-img')
]