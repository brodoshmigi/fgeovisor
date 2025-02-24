import rest_framework.permissions as rp
from django.shortcuts import redirect
from django.urls import reverse
from rest_framework.views import APIView
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from .models import UserPolygon
from .serializators import PolygonFromDbSerializer
from web_interface.staff import My_errors
from images.staff import delete_image, update_image_GEE


class CreatePolygon(APIView):
    """
    Методом научного тыка сохраняем данные из GeoJSON с фронта в БД ПОЛИГОН!!!!!!!!
    """
    parser_classes = [JSONParser]

    def post(self, request):
        """
        Желательно переписать по умному потом пж _(-_-)_ 
        Обясняю почему: мы получаем юзера, т.к. определяем его выше,
        Потом отрезаем от полученного geojson только нужную часть
        И потом преобразуем его в str потому что gdal/geos принимает...
        Строку...
        """
        # Обрабатываем GeoJSON здесь
        user = self.request.user
        polygon_instance = UserPolygon(owner=user,
                                       polygon_data=str(
                                           request.data['geometry']))
        polygon_instance.save()
        return Response(My_errors.error_send())

    def get(self, request):
        My_errors.tmp_context['create_error'] = True
        return redirect(reverse('map'))


class GetPolygons(APIView):
    """
    Возвращает полигоны пользователя
    """
    permission_classes = [rp.IsAuthenticated]

    def get(self, request):
        polygons_objects = UserPolygon.objects.filter(
            owner=self.request.user.id).all()
        polygons_serialized = PolygonFromDbSerializer(polygons_objects,
                                                      many=True)
        return Response(polygons_serialized.data)


class DeletePolygon(APIView):
    """
    Удаляет полигоны по запросу с фронта по id полигона, 
    т.к. у юзера есть доступ только к своему полигону
    """
    permission_classes = [rp.IsAuthenticated]

    def post(self, request):
        Polygons = UserPolygon.objects.filter(owner=self.request.user.id)
        # id должен быть, т.к. js отсылает тупо строчку - это неправильно
        # тесты с этим также не провести, и + в будущем нужно будет токен иметь
        polygon_instance = UserPolygon.get(polygon_id=request.data["id"])
        try:
            delete_image(polygon_instance)
        except Exception as e:
            print('Exception:', e)
        finally:
            polygon_instance.delete()
            return Response({"success": 'deleted'})


class UpdatePolygon(APIView):
    """
    Функция изменения полигонов
    """
    permission_classes = [rp.IsAuthenticated]

    def post(self, request):
        try:
            polygon_instance = UserPolygon.objects.get(
                polygon_id=request.data['id'])
            polygon_instance.polygon_data = str(request.data['geometry'])
            polygon_instance.save()
            update_image_GEE(polygon_instance)
            return Response({'success': 'updated'})
        except Exception:
            return Response({'lost': str(Exception)})
