from django.shortcuts import render
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import AnonymousUser, User

from rest_framework.permissions import (IsAuthenticatedOrReadOnly, AllowAny,
                                        IsAuthenticated)
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import (RetrieveModelMixin, CreateModelMixin,
                                   UpdateModelMixin)
from rest_framework.views import APIView
from rest_framework.response import Response

from .serializators import (AuthRegisterSerializator, AuthSerializator,
                            AuthSerializer)
from .staff import My_errors


class MapView(APIView):
    """ 
    main view that uses for session gui on client 
    we check request context and after manage our gui
    """

    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        user = self.request.user
        context = My_errors.tmp_context
        if user.username == AnonymousUser.username:
            context['auth_check'] = False
            return render(request,
                          'site_back/map_over_osm.html',
                          context=My_errors.error_send())
        context['auth_check'] = True
        context['is_staff'] = user.is_staff
        return render(request,
                      'site_back/map_over_osm.html',
                      context=My_errors.error_send())


class UserAuth(GenericViewSet, RetrieveModelMixin, CreateModelMixin):

    permission_classes = AllowAny

    serializer_class = AuthSerializer

    queryset = User.objects.all()

    def get_object(self):
        '''
        # !register is put
        if self.request.method.lower() in ['post', 'delete']:
            self.permission_classes = IsAuthenticated
        # we can validate request for register by this methods
        # self.get_parser_context, self.get_view_name|_description
        # but we can simply use path var in request object
        '''
        if 'register' not in self.request.path:
            self.permission_classes = IsAuthenticated
        return super().get_object()


class RegistrationView(APIView):
    """ Класс регистрации аккаунта с простейшей валидацией на стороне сервера """

    permission_classes = [AllowAny]

    def post(self, request):
        # Распакоука данных из сериализатора POST сессии
        data_serialized = AuthRegisterSerializator(data=request.data)
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

    permission_classes = [AllowAny]

    def post(self, request):
        data_serialized = AuthSerializator(data=request.data)
        data_serialized.is_valid()
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
