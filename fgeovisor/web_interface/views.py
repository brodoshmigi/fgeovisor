import rest_framework.permissions as rp
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import AnonymousUser, User
from rest_framework.views import APIView
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from .serializators import (UserRegistrationSerializator, UserLoginSerializator)
from .staff import My_errors


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
            return render(request, 'site_back/map_over_osm.html', 
                          context=My_errors.error_send())
            #return Response(My_errors.error_send())
        else:
            # описание состояния пользователя дл js
            context['auth_check'] = True
            context['is_staff'] = user.is_staff
            return render(request, 'site_back/map_over_osm.html', 
                          context=My_errors.error_send())

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

def logoutView(request):
    """
    Функции Копатыча | выход из аккаунта
    """
    logout(request)
    return redirect(reverse('map'))