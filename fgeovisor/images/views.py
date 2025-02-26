from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import (ListModelMixin, UpdateModelMixin,
                                   CreateModelMixin, DestroyModelMixin)
from rest_framework.status import (HTTP_200_OK, HTTP_204_NO_CONTENT,
                                   HTTP_201_CREATED,
                                   HTTP_500_INTERNAL_SERVER_ERROR,
                                   HTTP_400_BAD_REQUEST, HTTP_302_FOUND)

from rest_framework.response import Response
from polygons.models import UserPolygon
from web_interface.staff import My_errors
from .models import UserImage
from .serializators import ImageSerializator
from .staff import Image_GEE

DEFAULT_PARAMS = {'id': '', 'date': '', 'index': ''}


class UploadImg(GenericViewSet, ListModelMixin, UpdateModelMixin,
                CreateModelMixin, DestroyModelMixin):
    permission_classes = [IsAuthenticated]

    serializer_class = ImageSerializator

    def get_queryset(self):
        query_params = self.request.GET
        polygon_id, date, index = query_params.values()
        polygon_object = UserPolygon.objects.get(polygon_id=polygon_id)
        return UserImage.objects.filter(polygon_id=polygon_object,
                                        image_index=index.upper(),
                                        image_date=date)

    def list(self, request, *args, **kwargs) -> Response:
        query_params = self.request.GET
        query_equals = DEFAULT_PARAMS.keys() - query_params.keys()

        if not self.is_query_valid(self.request.GET, query_equals):
            error = {'error': f'You forgot {query_equals}'}
            return Response(status=HTTP_400_BAD_REQUEST, data=error)

        polygon_id, date, index = query_params.values()

        queryset: UserImage = self.filter_queryset(self.get_queryset())
        polygon_object = UserPolygon.objects.get(polygon_id=polygon_id)

        if not queryset:
            #если скачиваются ужен скачанные снимки, воможно проблема в датах
            image_object = Image_GEE(polygon_object,
                                     index=index.upper(),
                                     date_start=date)
            image_object.download_image()
            _image_object = image_object.calculate_index()
            return Response(status=HTTP_201_CREATED,
                            data={'url': _image_object.check_uri(request='1')},
                            headers={
                                'Cache-Control': 'no-cache, no-store, must-revalidate',
                                'Pragma': 'no-cache',
                                'Expires': '0'
                                })

        serializer = self.get_serializer(queryset, many=True)
        image_uri = queryset[0].check_uri(request='1')
        if image_uri is not None:
            return Response({'url': image_uri}, status=HTTP_302_FOUND)

        return Response(serializer.data, status=HTTP_204_NO_CONTENT)

    def is_query_valid(self, query_dict, q_e) -> bool:
        query_len = len(query_dict.keys())

        if query_len < 3 or query_len > 3:
            return False

        if q_e != set():
            return False

        return True


class ImageGEE(APIView):
    """
    Добавление фото из Google Earth Engine
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, id, date):
        polygons = UserPolygon.objects.filter(owner=self.request.user.id)
        polygon_instance = polygons.get(polygon_id=id)
        polygon_image = Image_GEE(polygon_instance, date_start=date)
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
