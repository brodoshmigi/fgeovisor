import rest_framework.permissions as rp
from rest_framework.views import APIView
from rest_framework.response import Response
from polygons.models import UserPolygon
from .models import UserImage
from .serializators import ImageSerializator
from .staff import Image_From_GEE
from web_interface.staff import My_errors


class UploadImg(APIView):
    """
    Функция добавления фото
    """
    permission_classes = [rp.IsAuthenticated]

    def get(self, request, id, date):
        polygons = UserPolygon.objects.filter(owner=self.request.user.id)
        polygon_instance = polygons.get(polygon_id=id)
        url = UserImage.objects.get(polygon=polygon_instance, date=date)
        image_serializator = ImageSerializator(url)
        return Response(image_serializator.data)


class ImageGEE(APIView):
    """
    Добавление фото из Google Earth Engine
    """

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
