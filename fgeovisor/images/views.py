import rest_framework.permissions as rp
from rest_framework.views import APIView
from rest_framework.response import Response
from polygons.models import Polygon
from .models import Image
from .serializators import ImageSerializator


class UploadImg(APIView):
    """
    Функция добавления фото
    """
    permission_classes = [rp.IsAuthenticated]

    def get(self, request, id):
        polygons = Polygon.objects.filter(owner=self.request.user.id)
        polygon_instance = polygons.get(polygon_id=id)
        url = Image.objects.get(polygon=polygon_instance)
        image_serializator = ImageSerializator(url)
        return Response(image_serializator.data)