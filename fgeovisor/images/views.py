from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import ListModelMixin
from rest_framework.status import (HTTP_204_NO_CONTENT, HTTP_201_CREATED,
                                   HTTP_400_BAD_REQUEST, HTTP_302_FOUND)

from rest_framework.response import Response

from polygons.models import UserPolygon
from web_interface.staff import is_query_valid
from .models import UserImage
from .serializators import ImageSerializator
from .GEE import Image_GEE
"""
⣿⣿⣿⣿⣿⣿⣿⠿⠿⢛⣋⣙⣋⣩⣭⣭⣭⣭⣍⣉⡛⠻⢿⣿⣿⣿⣿
⣿⣿⣿⠟⣋⣥⣴⣾⣿⣿⣿⡆⣿⣿⣿⣿⣿⣿⡿⠟⠛⠗⢦⡙⢿⣿⣿
⣿⡟⡡⠾⠛⠻⢿⣿⣿⣿⡿⠃⣿⡿⣿⠿⠛⠉⠠⠴⢶⡜⣦⡀⡈⢿⣿
⡿⢀⣰⡏⣼⠋⠁⢲⡌⢤⣠⣾⣷⡄⢄⠠⡶⣾⡀⠀⣸⡷⢸⡷⢹⠈⣿
⡇⢘⢿⣇⢻⣤⣠⡼⢃⣤⣾⣿⣿⣿⢌⣷⣅⡘⠻⠿⢛⣡⣿⠀⣾⢠⣿ 
⣷⠸⣮⣿⣷⣨⣥⣶⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡟⢁⡼⠃⣼⣿ 
⡟⠛⠛⠛⣿⠛⠛⢻⡟⠛⠛⢿⡟⠛⠛⡿⢻⡿⠛⡛⢻⣿⠛⡟⠛⠛⢿ 
⡇⢸⣿⠀⣿⠀⠛⢻⡇⠸⠃⢸⡇⠛⢛⡇⠘⠃⢼⣷⡀⠃⣰⡇⠸⠇⢸ 
⡇⢸⣿⠀⣿⠀⠛⢻⡇⢰⣿⣿⡇⠛⠛⣇⢸⣧⠈⣟⠃⣠⣿⡇⢰⣾⣿ 
⣿⣿⣿⠘⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⢋⣿⠙⣷⢸⣷⠀⣿⣿⣿ 
⣿⣿⣿⡇⢻⣿⣿⣿⡿⠿⢿⣿⣿⣿⠟⠋⣡⡈⠻⣇⢹⣿⣿⢠⣿⣿⣿ 
⣿⣿⣿⣿⠘⣿⣿⣿⣿⣯⣽⣉⣿⣟⣛⠷⠙⢿⣷⣌⠀⢿⡇⣼⣿⣿⣿ 
⣿⣿⣿⡿⢀⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣶⣤⡙⢿⢗⣀⣁⠈⢻⣿⣿ 
⣿⡿⢋⣴⣿⣎⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣦⡉⣯⣿⣷⠆⠙⢿ 
⣏⠀⠈⠧⠡⠉⠙⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠃⠉⢉⣁⣀⣀⣾
"""

DEFAULT_PARAMS = {'id': '', 'date': '', 'index': ''}

NO_CACHE_HEADERS = {
    'Cache-Control': 'no-cache, no-store, must-revalidate',
    'Pragma': 'no-cache',
    'Expires': '0'
}


class UploadImgViewSet(GenericViewSet, ListModelMixin):
    permission_classes = [IsAuthenticated]

    serializer_class = ImageSerializator

    # По правилам drf, каждый запрос должен перевычеслять queryset
    # all там и тут передают
    queryset = UserImage.objects.all()

    # Если хочется соблюдать реальный MVC, тогда нужно использовать ->
    # filter_backends = [и создать свой бекенд для фильтрации]
    # И в нашем случае, раз мы используем, что-то типо get_obj 10 из 10,
    # Нужно будет переписать логику чисто get_object, а queryset оставить серьезным дядям
    def get_queryset(self, polygon_id, date, index):
        return self.queryset.all().filter(polygon_id__pk=polygon_id,
                                          image_index=index.upper(),
                                          image_date=date)

    # 32 + 4 < 50
    def list(self, request, *args, **kwargs) -> Response:
        query_params = self.request.GET
        query_equals = DEFAULT_PARAMS.keys() - query_params.keys()

        if is_query_valid(query_params, query_equals):

            polygon_id, date, index = query_params.values()

            queryset = self.filter_queryset(
                self.get_queryset(polygon_id=polygon_id,
                                  date=date,
                                  index=index))

            serializer = self.get_serializer(queryset, many=True)

            # bool(queryset) >= exists exists exists if 67, else no
            if not bool(queryset):
                # если скачиваются ужен скачанные снимки, воможно проблема в датах
                obj = self.get_image_from_google(polygon_id=polygon_id,
                                                 date=date,
                                                 index=index)
                return Response(
                    status=HTTP_201_CREATED,
                    data={"url": obj.check_uri()},
                    # headers={headers={"Location": obj.check_uri()}.update(NO_CACHE)
                )

            obj = queryset.first()

            if obj is not None:
                return Response(
                    status=HTTP_302_FOUND,
                    data={"url": obj.check_uri()},
                    # headers={"Location": obj.check_uri()}.update(NO_CACHE)
                )

            return Response(status=HTTP_204_NO_CONTENT, data=serializer.data)

        error = {"error": f"You forgot {query_equals}"}
        return Response(status=HTTP_400_BAD_REQUEST, data=error)

    # overload
    def get_image_from_google(self, polygon_id, date, index):
        """ Зубов во рту должно быть столько, сколько ты можешь себе позволить вылечить. """
        polygon_obj = UserPolygon.objects.all().filter(polygon_id=polygon_id)
        image_object = Image_GEE(polygon_obj,
                                 index=index.upper(),
                                 date_start=date)
        image_object.download_image()
        _image_object = image_object.calculate_index()
        image_object.remove_bands()
        return _image_object
