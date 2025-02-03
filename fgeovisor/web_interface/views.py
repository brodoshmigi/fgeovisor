import rest_framework.permissions as rp
from django.shortcuts import render
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import AnonymousUser

import rest_framework.permissions as rp
from rest_framework.views import APIView
from rest_framework.response import Response

from .serializators import (UserRegistrationSerializator,
                            UserLoginSerializator)
from .staff import My_errors
import requests

GOOGLE_API_KEY = settings.GOOGLE_CALENDAR_API_KEY  # Храним API-ключ в настройках
CALENDAR_ID = settings.GOOGLE_CALENDAR_ID  # ID календаря
""" Классы представлений, которые отрабатывают обращения клиента """


class MapView(APIView):
    """ Рендерит карту по запросу и проверяет авторизован пользователь или нет """

    permission_classes = [rp.IsAuthenticatedOrReadOnly]

    # ТУТА ПРОВЕРКА ГУТ ГУТ
    def get(self, request):
        user = self.request.user
        context = My_errors.tmp_context
        if user.username == AnonymousUser.username:
            # описание состояния пользователя дл js
            context['auth_check'] = False
            return render(request,
                          'site_back/map_over_osm.html',
                          context=My_errors.error_send())
            #return Response(My_errors.error_send())
        else:
            # описание состояния пользователя дл js
            context['auth_check'] = True
            context['is_staff'] = user.is_staff
            return render(request,
                          'site_back/map_over_osm.html',
                          context=My_errors.error_send())


class RegistrationView(APIView):
    """ Класс регистрации аккаунта с простейшей валидацией на стороне сервера """

    permission_classes = [rp.AllowAny]

    def post(self, request):
        # Распакоука данных из сериализатора POST сессии
        data_serialized = UserRegistrationSerializator(data=request.data)
        if data_serialized.is_valid():
            # Сохранение в БД
            data_serialized.save()
        else:
            # отрисовка карты, отправка ошибки на фронт
            My_errors.tmp_context['is_vallid_error'] = True
            return Response(My_errors.error_send())
            #return Response(My_errors.error_send())
        username = data_serialized.data.get('username')
        password = request.data['password']
        user = authenticate(request, username=username, password=password)
        login(request, user)
        My_errors.tmp_context['auth_check'] = True
        return Response(My_errors.error_send())


class LoginView(APIView):
    """ Класс логина в аккаунт """

    permission_classes = [rp.AllowAny]

    def post(self, request):
        # Распакоука данных из сериализатора POST сессии
        data_serialized = UserLoginSerializator(data=request.data)
        data_serialized.is_valid()
        # автовход после регистрации
        username = data_serialized.data.get('username')
        password = data_serialized.data.get('password')
        user = authenticate(username=username, password=password)
        try:
            login(request, user)
            My_errors.tmp_context['auth_check'] = True
            My_errors.tmp_context['is_staff'] = self.request.user.is_staff
            return Response(My_errors.error_send())
        except AttributeError:
            # отрисовка карты, отправка ошибки на фронт
            My_errors.tmp_context['login_error'] = True
            return Response(My_errors.error_send())


class LogoutView(APIView):
    """ Функции Копатыча | выход из аккаунта """

    def post(self, request):
        logout(request)
        return Response("")

def get_calendar_events(request):
    """Функция Карыча | Google Calendar"""
    url = (f'https://www.googleapis.com/calendar/v3/calendars/;'
          f'{CALENDAR_ID}/events?key={GOOGLE_API_KEY}')

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return JsonResponse(data)
    
    except requests.exceptions.RequestException as e:
        return JsonResponse({"error": "Ошибка при запросе к Google API", "details": str(e)}, status=500)
