import rest_framework.permissions as rp
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import AnonymousUser, User
from rest_framework import generics, status
from rest_framework.views import APIView
from django.urls import reverse
from rest_framework.response import Response
from .models import Polygon
from .serializators import (PolygonOwnerSerializator, UserRegistrationSerializator, UserLoginSerializator,
                            My_errors)

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
        context = My_errors.tmp_context
        if user.username == AnonymousUser.username:
            
            # описание состояния пользователя дл js
            context['auth_check'] = False

            return render(request, "site_back/map_over_osm.html", context=My_errors.error_send())
            #return Response(My_errors.error_send())
        else:
            """
            Возвращаем дату из сериализатора
            """
            # описание состояния пользователя дл js
            context['auth_check'] = True
            context['is_staff'] = user.is_staff
            
            return redirect(reverse('map'), context=My_errors.error_send())
            #return Response(My_errors.error_send())
        
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
            My_errors.tmp_context['login_error'] = True
            return redirect(reverse('map'))
    
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
Функции КОпатыча
"""
def logoutView(request):
    logout(request)
    return redirect(reverse('map'))
