import logging

from django.contrib.gis.geos import Polygon

from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import (ListModelMixin, UpdateModelMixin,
                                   CreateModelMixin, DestroyModelMixin)

from rest_framework.response import Response

from rest_framework.renderers import JSONRenderer
from rest_framework.permissions import IsAuthenticated

from rest_framework.status import (HTTP_200_OK, HTTP_204_NO_CONTENT,
                                   HTTP_201_CREATED,
                                   HTTP_500_INTERNAL_SERVER_ERROR,
                                   HTTP_400_BAD_REQUEST, HTTP_403_FORBIDDEN)

from staff.core.image_helper import delete_image, update_image

from .models import UserPolygon, User, Bounds
from .serializators import GeoJSONSerializer
"""
— Я исполню три ваших желания. Но очень плохо.
— А ты кто?
— Джун.

░░░░░░░░░░░░▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄░░░░░░░░░░░░░
░░░░░▄▄▄▄█▀▀▀░░░░░░░░░░░░▀▀██░░░░░░░░░░░
░░▄███▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄█▄▄▄░░░░░░░
▄▀▀░█░░░░▀█▄▀▄▀██████░▀█▄▀▄▀████▀░░░░░░░
█░░░█░░░░░░▀█▄█▄███▀░░░░▀▀▀▀▀▀▀░▀▀▄░░░░░
█░░░█░▄▄▄░░░░░░░░░░░░░░░░░░░░░▀▀░░░█░░░░
█░░░▀█░░█░░░░▄░░░░▄░░░░░▀███▀░░░░░░░█░░░
█░░░░█░░▀▄░░░░░░▄░░░░░░░░░█░░░░░░░░█▀▄░░
░▀▄▄▀░░░░░▀▀▄▄▄░░░░░░░▄▄▄▀░▀▄▄▄▄▄▀▀░░█░░
░█▄░░░░░░░░░░░░▀▀▀▀▀▀▀░░░░░░░░░░░░░░█░░░
░░█░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░▄██░░░░
░░▀█▄░░░░░░░░░░░░░░░░░░░░░░░░░▄▀▀░░░▀█░░
█▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀█
█░░█▀▄ █▀▀ █▀█ █░░░░█░▄░█ █ ▀█▀ █░█░░█ ▀█▀░█
█░░█░█ █▀▀ █▀█ █░░░░▀▄▀▄▀ █ ░█░ █▀█░░█ ░█░░█
█░░▀▀░ ▀▀▀ ▀░▀ ▀▀▀░░░▀░▀░ ▀ ░▀░ ▀░▀░░▀ ░▀░░█
▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀
"""

logger = logging.getLogger(__name__)


class PolygonsViewSet(GenericViewSet, ListModelMixin, UpdateModelMixin,
                      CreateModelMixin, DestroyModelMixin):
    """ CRUD by DRF-viewset """

    permission_classes = [IsAuthenticated]

    serializer_class = GeoJSONSerializer

    renderer_classes = [JSONRenderer]

    queryset = UserPolygon.objects.all()

    def get_queryset(self):
        queryset = UserPolygon.objects.all().filter(owner=self.request.user.id)
        code = self.request.GET.get('code')
        if code:
            queryset = queryset.filter(district__code=code)
        return queryset
    
    # Для логирования методов super класса нужно их менять
    def create(self, request, *args, **kwargs):
        input_polygon = Polygon(*self.request.data['geometry']['coordinates'])
        if self.check_district_valid(input_polygon):
            if self.check_create_valid(input_polygon):
                return super().create(request, *args, **kwargs)
        return Response(status=HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        input_polygon = Polygon(*self.request.data['geometry']['coordinates'])
        if self.check_district_valid(input_polygon):
            if self.check_update_valid(input_polygon):
                polygon_object = self.get_object()
                try:
                    delete_image(polygon_object.polygon_id)
                except Exception as e:
                    print('except: ', e)
                finally:
                    return super().update(request, *args, **kwargs)
        return Response(status=HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        polygon_object = self.get_object()

        # we can look for instance relation
        # and find all images, its a real solution
        try:
            delete_image(polygon_object.polygon_id)
        except Exception as e:
            print('except: ', e)
        finally:
            self.perform_destroy(polygon_object)

        return Response(status=HTTP_204_NO_CONTENT)

    def perform_create(self, serializer):
        serializer.save(
            owner=self.request.user,
            district=Bounds.objects.get(code=self.request.data['code']))

    def perform_update(self, serializer):
        serializer.save(owner=self.request.user)

    # Всю валидацию можно перенести в constraints в БД или в МОДЕЛИ ЙОООУ
    def check_district_valid(self, input_polygon) -> bool:
        district_geom = Bounds.objects.filter(code=int(
            self.request.data['code']),
                                              geom__contains=input_polygon)
        #logger.debug("Создание полигона: проверка на регион %s",
        #             district_geom.exists())
        return district_geom.exists()

    def check_create_valid(self, input_polygon) -> bool:
        polygon_objects = UserPolygon.objects.filter(
            polygon_data__intersects=input_polygon)
        #logger.debug("Создание полигона: проверка на пересечения %s",
        #             polygon_objects.exists())
        return not polygon_objects.exists()

    def check_update_valid(self, input_polygon) -> bool:
        polygon_objects = UserPolygon.objects.exclude(
            polygon_id=self.kwargs['pk']).filter(
                polygon_data__intersects=input_polygon)
        #logger.debug("Обновление полигона: проверка на пересечение %s",
        #             polygon_objects.exists())
        return not polygon_objects.exists()


class PolygonsView(APIView):
    """ Low-level DRF, тот же CRUD, но на низком уровне """
    # на 100 коммитов устарел
    permission_classes = [IsAuthenticated]

    def get(self, request):
        polygons_objects = UserPolygon.objects.filter(
            owner=self.request.user.id)

        if polygons_objects:
            polygons_serialize = GeoJSONSerializer(polygons_objects, many=True)
            return Response(polygons_serialize.data, status=HTTP_200_OK)

        return Response(status=HTTP_204_NO_CONTENT)

    def post(self, request):
        """ geos принимает в себя строку запомнить! """
        serializator = GeoJSONSerializer(request.data)

        if serializator.is_valid(raise_exception=True):
            serializator.save()
            return Response(status=HTTP_201_CREATED)

        return Response(status=HTTP_400_BAD_REQUEST)

    def delete(self, request):
        pk = request.GET.get('id')

        if pk is None:
            return Response(status=HTTP_400_BAD_REQUEST)

        polygon_object = UserPolygon.objects.get(owner=self.request.user.id,
                                                 polygon_id=pk)

        try:
            delete_image(polygon_object)
        except Exception as e:
            print('Exception: ', e)
        finally:
            polygon_object.delete()

        return Response(status=HTTP_204_NO_CONTENT)

    def put(self, request):
        try:
            pk = request.GET.get('id')

            if pk is None:
                return Response(status=HTTP_400_BAD_REQUEST)

            polygon_object = UserPolygon.objects.get(
                owner=self.request.user.id, polygon_id=pk)
            polygon_object.polygon_data = str(request.data['geometry'])
            polygon_object.save()
            update_image(polygon_object)
            return Response(status=HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)},
                            status=HTTP_500_INTERNAL_SERVER_ERROR)
