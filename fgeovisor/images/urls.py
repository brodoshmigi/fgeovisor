from django.urls import path

from .views import UploadImgViewSet

# query-params: ?id=id&date=date&index=index
urlpatterns = [
    path('get-img',
         UploadImgViewSet.as_view({'get': 'list'}),
         name='get-img'),
]
