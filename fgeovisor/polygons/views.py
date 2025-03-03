from django.contrib.gis.geos import Polygon

from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import (ListModelMixin, UpdateModelMixin,
                                   CreateModelMixin, DestroyModelMixin)
from rest_framework.status import (HTTP_200_OK, HTTP_204_NO_CONTENT,
                                   HTTP_201_CREATED,
                                   HTTP_500_INTERNAL_SERVER_ERROR,
                                   HTTP_400_BAD_REQUEST)
from rest_framework.response import Response

from images.staff import delete_image, update_image_GEE
from .models import UserPolygon, User
from .serializators import GeoJSONSerializer


class PolygonsViewSet(GenericViewSet, ListModelMixin, UpdateModelMixin,
                      CreateModelMixin, DestroyModelMixin):
    """ CRUD by DRF-viewset """

    permission_classes = [IsAuthenticated]

    serializer_class = GeoJSONSerializer

    def get_queryset(self):
        user_id = self.request.user.id
        return UserPolygon.objects.filter(owner=user_id)

    def create(self, request, *args, **kwargs):
        if self.check_create_valid():
            return Response(status=HTTP_400_BAD_REQUEST)
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        if self.check_update_valid():
            return Response(status=HTTP_400_BAD_REQUEST)
        # but need to add validation in perform_update
        # because users should not update polygons
        # unless they are the ones who created them.
        polygon_object = self.get_object()
        try:
            delete_image(polygon_object.polygon_id)
        except Exception as e:
            print('except: ', e)
        finally:
            return super().update(request, *args, **kwargs)

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
        serializer.save(owner=self.request.user)

    def check_create_valid(self):
        input_polygon = Polygon(*self.request.data['geometry']['coordinates'])
        polygon_objects = UserPolygon.objects.filter(
            polygon_data__intersects=input_polygon)
        return polygon_objects.exists()

    def check_update_valid(self):
        input_polygon = Polygon(*self.request.data['geometry']['coordinates'])
        polygon_objects = UserPolygon.objects.exclude(
            polygon_id=self.request.data['id']).filter(
                polygon_data__intersects=input_polygon)
        return polygon_objects.exists()


class PolygonsView(APIView):
    """ Low-level DRF, тот же CRUD, но на низком уровне """
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
            update_image_GEE(polygon_object)
            return Response(status=HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)},
                            status=HTTP_500_INTERNAL_SERVER_ERROR)
