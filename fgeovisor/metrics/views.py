import logging

from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import (ListModelMixin, UpdateModelMixin,
                                   CreateModelMixin, DestroyModelMixin)

from rest_framework.response import Response

from rest_framework.renderers import JSONRenderer
from rest_framework.permissions import IsAuthenticated

from rest_framework.status import (HTTP_200_OK, HTTP_204_NO_CONTENT,
                                   HTTP_201_CREATED,
                                   HTTP_500_INTERNAL_SERVER_ERROR,
                                   HTTP_400_BAD_REQUEST, HTTP_403_FORBIDDEN,
                                   HTTP_302_FOUND)

from polygons.models import UserPolygon
from web_interface.staff import is_query_valid
from images.GEE import Image_GEE

from .models import Metrics
from .serializators import MetricSerializator
from .staff import (calculate_default_polygon_stats, compute_index_stats_range)
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

logger = logging.getLogger(__name__)


class MetricsViewSet(GenericViewSet, ListModelMixin):

    permission_classes = [IsAuthenticated]

    serializer_class = MetricSerializator

    # ыыы уебище
    renderer_classes = [JSONRenderer]

    queryset = Metrics.objects.all()

    def get_queryset(self, polygon_id, start, end):
        return self.queryset.all().filter(polygon_id__pk=polygon_id,
                                          date__range=(start, end))

    # 42 < 50
    def list(self, request, *args, **kwargs) -> Response:
        query_params = self.request.GET
        query_equals = DEFAULT_PARAMS.keys() - query_params.keys()

        if is_query_valid(query_params, query_equals, 3):

            polygon_id, start, end = query_params.values()
            # logger.debug("%s %s %s", polygon_id, start, end)

            queryset = self.filter_queryset(
                self.get_queryset(polygon_id=polygon_id, start=start, end=end))

            if not bool(queryset):
                # obj = celery
                poly_obj = UserPolygon.objects.all().filter(
                    polygon_id=polygon_id).first()

                calculate_default_polygon_stats(obj=poly_obj, date=start)
                queryset = compute_index_stats_range(obj=poly_obj,
                                                   start=start,
                                                   end=end)

                # Внутрь нужно передавать iterable obj если many=True
                serializer = self.get_serializer(queryset, many=True)

                # logger.debug("%s", serializer.data)

                return Response(
                    status=HTTP_201_CREATED,
                    data=serializer.data,
                    # headers={headers={"Location": }.update(NO_CACHE)
                )

            # Вы не поверите товарищ полицейский, тут MetricSerializator
            # вдруг превращается в ListSerializator и начинает
            # оборачивать все в списки...
            serializer = self.get_serializer(queryset, many=True)

            return Response(status=HTTP_200_OK, data=serializer.data)

        # logger.debug("%s", serializer.data)
        error = {"error": f"You forgot {query_equals}"}
        return Response(status=HTTP_400_BAD_REQUEST, data=error)
