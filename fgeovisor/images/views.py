from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import (RetrieveModelMixin, UpdateModelMixin,
                                   CreateModelMixin, DestroyModelMixin)
from rest_framework.status import (HTTP_200_OK, HTTP_204_NO_CONTENT,
                                   HTTP_201_CREATED,
                                   HTTP_500_INTERNAL_SERVER_ERROR,
                                   HTTP_400_BAD_REQUEST)

from rest_framework.response import Response
from polygons.models import UserPolygon
from web_interface.staff import My_errors
from .models import UserImage
from .serializators import ImageSerializator
from .staff import Image_From_GEE


class UploadImg(GenericViewSet, RetrieveModelMixin, UpdateModelMixin, 
                CreateModelMixin, DestroyModelMixin):
    permission_classes = [IsAuthenticated]

    serializer_class = ImageSerializator

    def get_queryset(self):
        query_params = self.request.GET
        polygon_id, index, date = query_params['id'], 
        query_params['index'], query_params['date']
        
        return UserPolygon.objects.get(polygon_id=polygon_id, 
                                          image_index=index, 
                                          image_date=date)


class ImageGEE(APIView):
    """
    Добавление фото из Google Earth Engine
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, id, date):
        polygons = UserPolygon.objects.filter(owner=self.request.user.id)
        polygon_instance = polygons.get(polygon_id=id)
        polygon_image = Image_From_GEE(polygon_instance, date_start=date)
        """
        try:
            polygon_image.download_image()
            polygon_image.visualization()
            My_errors.tmp_context['photo'] = True
            return Response(My_errors.error_send())
        except Exception:
            My_errors.tmp_context['photo'] = False
            return Response(status=507)
        """
        polygon_image.download_image()
        polygon_image.visualization()
        My_errors.tmp_context['photo'] = True
        return Response(My_errors.error_send())


