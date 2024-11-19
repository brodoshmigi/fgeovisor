from django.urls import path
from . import views

urlpatterns = [
    path('get-img/', views.UploadImg.as_view(), name='upload-img')
]