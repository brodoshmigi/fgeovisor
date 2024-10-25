import json
import rest_framework.permissions as rp
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import AnonymousUser, User
from rest_framework import generics, status
from rest_framework.views import APIView
from django.urls import reverse
from rest_framework.response import Response
from .models import Polygon
from .serializators import PolygonOwnerSerializator, UserRegistrationSerializator, UserLoginSerializator


"""
Request запросы на вывод HTML файлов
"""

class MapView(APIView):
    """
    Рендерит карту по запросу и проверяет авторизован пользователь или нет
    """
    permission_classes = [rp.IsAuthenticatedOrReadOnly]

    # ТУТА ПРОВЕРКА ГУТ ГУТ
    def get(self, request):
        user = self.request.user
        if user.username == AnonymousUser.username:
            """
            Просто возвращаем карту 
            
            """
            context={'auth_check': False,
                    'is_staff': False}

            return render(request, "site_back/map_over_osm.html", context=context)
            #return Response(user.username)
        else:
            """
            Возвращаем дату из сериализатора
            """
            # // TO
            context={'auth_check': True,
                     'is_staff': user.is_staff}
            
            # DO //
            return render(request, "site_back/map_over_osm.html", context=context)
            #return Response(user.username)
        
class RegistrationView(APIView):
    """
    Функция регистрации аккаунта с простейшей валидацией на стороне сервера
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
            context={"auth_check": False,
                     "is_staff": False,
                    'is_vallid_error': True}
            return render(request, "site_back/map_over_osm.html", context=context)
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        login(request, user)   
        return redirect(reverse('map'))

class LoginView(APIView):
    """
    Функция логина в аккаунт
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
            context={"auth_check": False,
                     "is_staff": False,
                    'login_error': True}
            return render(request, "site_back/map_over_osm.html", context=context)
  
    
"""
Request запросы на JSON
"""

class UserPolygonsView(generics.ListAPIView):
    """
    Отправляет JSON от сериализатора по запросу 
    """
    serializer_class = PolygonOwnerSerializator
    queryset = Polygon.objects.all()

"""
Класс Трах-Трахыча
"""
class createView(APIView):
    
    def post(self, request):
        data = request.data
        # Обрабатываем GeoJSON здесь
        return Response({'status': 'success', 'message': 'GeoJSON received!'})

"""
Функции КОпатыча
"""
def logoutView(request):
    logout(request)
    return redirect(reverse('map'))
