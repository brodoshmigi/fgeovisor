from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import (ListModelMixin, UpdateModelMixin,
                                   CreateModelMixin, DestroyModelMixin)
from rest_framework.status import (HTTP_200_OK, HTTP_204_NO_CONTENT,
                                   HTTP_201_CREATED,
                                   HTTP_500_INTERNAL_SERVER_ERROR,
                                   HTTP_400_BAD_REQUEST, HTTP_403_FORBIDDEN)
from rest_framework.response import Response

from rest_framework.response import Response

from polygons.models import UserPolygon
from web_interface.staff import is_query_valid
from .models import Metrics
from .serializators import MetricSerializator
from images.GEE import Image_GEE
"""
██░└┐░░░░░░░░░░░░░░░░░┌┘░██
██░░└┐░░░░░░░░░░░░░░░┌┘░░██
██░░┌┘▄▄▄▄▄░░░░░▄▄▄▄▄└┐░░██
██▌░│██████▌░░░▐██████│░▐██
███░│▐███▀▀░░▄░░▀▀███▌│░███
██▀─┘░░░░░░░▐█▌░░░░░░░└─▀██
██▄░░░▄▄▄▓░░▀█▀░░▓▄▄▄░░░▄██
████▄─┘██▌░░░░░░░▐██└─▄████
█████░░▐█─┬┬┬┬┬┬┬─█▌░░█████
████▌░░░▀┬┼┼┼┼┼┼┼┬▀░░░▐████
█████▄░░░└┴┴┴┴┴┴┴┘░░░▄█████
"""

DEFAULT_PARAMS = {'id': '', 'from': '', 'to': ''}


class MetricsViewSet(GenericViewSet, ListModelMixin):

    permission_classes = [IsAuthenticated]

    serializer_class = MetricSerializator

    queryset = Metrics.objects.all()

    def get_queryset(self, polygon_id, start, end):
        return self.queryset.all().filter(polygon_id__pk=polygon_id,
                                          date__range=(start, end))

    def list(self, request, *args, **kwargs) -> Response:
        query_params = self.request.GET
        query_equals = DEFAULT_PARAMS.keys() - query_params.keys()

        if is_query_valid(query_params, query_equals):

            polygon_id, start, end = query_params.values()

            queryset = self.filter_queryset(
                self.get_queryset(polygon_id=polygon_id, start=start, end=end))

            serializer = self.get_serializer(queryset, many=True)

            if not bool(queryset):
                # obj = celery

                return Response(
                    status=HTTP_201_CREATED,
                    data=serializer.data,
                    # headers={headers={"Location": obj.check_uri()}.update(NO_CACHE)
                )

            obj = queryset.first()

            if obj is not None:
                return Response(
                    status=HTTP_302_FOUND,
                    data=serializer.data,
                    # headers={"Location": obj.check_uri()}.update(NO_CACHE)
                )

            return Response(status=HTTP_204_NO_CONTENT, data=serializer.data)

        error = {"error": f"You forgot {query_equals}"}
        return Response(status=HTTP_400_BAD_REQUEST, data=error)
