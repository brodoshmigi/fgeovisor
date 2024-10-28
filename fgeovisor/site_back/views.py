import rest_framework.permissions as rp
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import AnonymousUser, User
from rest_framework.views import APIView
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from .models import Polygon
from .serializators import (UserRegistrationSerializator, UserLoginSerializator,)
from .staff import My_errors, get_polygons


"""
Классы представлений, которые отрабатывают обращения клиента
"""

class MapView(APIView):
    """
    Рендерит карту по запросу и проверяет авторизован пользователь или нет
    """
    permission_classes = [rp.IsAuthenticatedOrReadOnly]

    # ТУТА ПРОВЕРКА ГУТ ГУТ
    def get(self, request):
        user = self.request.user
        context = My_errors.tmp_context
        if user.username == AnonymousUser.username:
            # описание состояния пользователя дл js
            context['auth_check'] = False
            return render(request, 'site_back/map_over_osm.html', context=My_errors.error_send())
            #return Response(My_errors.error_send())
        else:
            # описание состояния пользователя дл js
            context['auth_check'] = True
            context['is_staff'] = user.is_staff
            return render(request, 'site_back/map_over_osm.html', context=My_errors.error_send())

class RegistrationView(APIView):
    """
    Класс регистрации аккаунта с простейшей валидацией на стороне сервера
    """
    permission_classes = [rp.AllowAny]

    def post(self, request):
        # Распакоука данных из сериализатора POST сессии
        registrationData = UserRegistrationSerializator(data=request.data)
        if registrationData.is_valid():
            # Сохранение в БД
            registrationData.save()
        else: 
            # отрисовка карты, отправка ошибки на фронт
            My_errors.tmp_context['is_vallid_error'] = True
            return redirect(reverse('map'))
            #return Response(My_errors.error_send())
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        login(request, user)   
        return redirect(reverse('map'))

class LoginView(APIView):
    """
    Класс логина в аккаунт
    """ 
    permission_classes = [rp.AllowAny]

    def post(self, request):
        # Распакоука данных из сериализатора POST сессии
        loginData = UserLoginSerializator(data=request.data)
        loginData.is_valid()
        #автовход после регистрации
        username = loginData.data.get('username')
        password = loginData.data.get('password')
        user = authenticate(username=username, password=password)
        try: 
            login(request, user)
            return redirect(reverse('map'))
        except AttributeError:
            # отрисовка карты, отправка ошибки на фронт
            My_errors.tmp_context['login_error'] = True
            return redirect(reverse('map'))


class CreatePolygon(APIView):
    """
    Методом научного тыка сохраняем данные из GeoJSON с фронта в БД ПОЛИГОН!!!!!!!!
    """
    parser_classes = [JSONParser]
    
    def post(self, request):
        """
        Желательно переписать по умному потом пж _(-_-)_ 
        Обясняю почему: мы получаем юзера, т.к. определяем его выше,
        потом отрезаем от полученного geodjson только нужную часть
        и потом преобразуем его в str потому что gdal/geos принимает...
        строку...
        """
        # Обрабатываем GeoJSON здесь
        user = self.request.user
        polygonInstance = Polygon(login=user, polygon_data=str(
                                    request.data['geometry']))
        polygonInstance.save()
        return Response({'status': 'Polygon saved!'})

    def get(self, request):
        My_errors.tmp_context['create_error'] = True
        return redirect(reverse('map'))

class GetPolygons(APIView):
    """
    Возвращает полигоны пользователя
    """
    permission_classes = [rp.IsAuthenticated]

    def get(self, request):
        polygons = get_polygons(self.request.user.id)
        return Response(polygons)

class DeletePolygon(APIView):
    """
    Удаляет полигоны по запросу с фронта по id полигона, т.к. у юзера есть доступ только к своему полигону
    """
    permission_classes = [rp.IsAuthenticated]
    
    def post(self, request):
        Polygons = Polygon.objects.filter(login=self.request.user.id)
        Polygons.get(polygon_id=request.data).delete()
        return Response({"success": True})


def logoutView(request):
    """
    Функции Копатыча | выход из аккаунта
    """
    logout(request)
    return redirect(reverse('map'))