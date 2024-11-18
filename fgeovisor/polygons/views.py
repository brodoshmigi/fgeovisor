import rest_framework.permissions as rp
from django.shortcuts import render, redirect
from django.urls import reverse
from rest_framework.views import APIView
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from .models import Polygon
from images.models import Image
from .serializators import PolygonFromDbSerializer
from web_interface.staff import My_errors
from images.staff import Image_From_GEE

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
        polygonInstance = Polygon(owner=user, polygon_data=str(
                                    request.data['geometry']))
        polygonInstance.save()
        polygon_image = Image_From_GEE(polygonInstance)
        polygon_image.download_image()
        polygon_image.visualization()
        return Response(request.data)

    def get(self, request):
        My_errors.tmp_context['create_error'] = True
        return redirect(reverse('map'))

class GetPolygons(APIView):
    """
    Возвращает полигоны пользователя
    """
    permission_classes = [rp.IsAuthenticated]

    def get(self, request):
        polygons_objects = Polygon.objects.filter(owner=self.request.user.id).all()
        polygons_objects = PolygonFromDbSerializer(polygons_objects, many=True)
        return Response(polygons_objects.data, content_type='application/json')

class DeletePolygon(APIView):
    """
    Удаляет полигоны по запросу с фронта по id полигона, 
    т.к. у юзера есть доступ только к своему полигону
    """
    permission_classes = [rp.IsAuthenticated]
    
    def post(self, request):
        Polygons = Polygon.objects.filter(owner=self.request.user.id)
        # id должен быть, т.к. js отсылает тупо строчку - это неправильно
        # тесты с этим также не провести, и + в будущем нужно будет токен иметь
        Polygons.get(polygon_id=request.data["id"]).delete()
        return Response({"success": 'deleted'}, content_type='application/json')

class UpdatePolygon(APIView):
    """
    Функция изменения полигонов
    """
    permission_classes = [rp.IsAuthenticated]

    def post(self, request):
        try:
            polygon = Polygon.objects.get(polygon_id=request.data['id'])
            polygon.polygon_data=str(request.data['geometry'])
            polygon.save()
            return Response({'success': 'updated'}, content_type='application/json')
        except Exception:
            return Response({'lost': Exception}, content_type='application/json')

