import logging
from typing import Dict

from django.shortcuts import render, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import AnonymousUser, User

from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import (RetrieveModelMixin, CreateModelMixin)
from rest_framework.views import APIView

from rest_framework.response import Response

from rest_framework.permissions import (IsAuthenticatedOrReadOnly, AllowAny,
                                        IsAuthenticated)

from rest_framework.status import (HTTP_205_RESET_CONTENT,
                                   HTTP_400_BAD_REQUEST, HTTP_403_FORBIDDEN,
                                   HTTP_401_UNAUTHORIZED, HTTP_201_CREATED,
                                   HTTP_404_NOT_FOUND,
                                   HTTP_500_INTERNAL_SERVER_ERROR,
                                   HTTP_302_FOUND, HTTP_200_OK)

from staff.core.errors import ErrorSnapshot

from .serializators import (AuthRegisterSerializator, AuthSerializator,
                            AuthSerializer, ResetPasswordSerializer,
                            LoginSerializer)


logger = logging.getLogger(__name__)


class MapView(APIView):
    """ 
    main view that uses for session gui on client 
    we check request context and after manage our gui
    """

    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        user = self.request.user
        is_anonymous = user.username != AnonymousUser.username
        error_sender = ErrorSnapshot()
        error_sender.set_error("auth_check", is_anonymous)
        error_sender.set_error("is_staff", user.is_staff)
        return render(request,
                      "site_back/map_over_osm.html",
                      context=error_sender.send())


class UserAuthViewSet(GenericViewSet, RetrieveModelMixin, CreateModelMixin):

    permission_classes = [AllowAny]

    serializer_class = AuthSerializer

    # lookup_field = "token" # def pk
    # lookup_url_kwarg = "token" # def None"

    queryset = User.objects.all()

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())

        # Perform the lookup filtering.
        # lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field

        filter_kwargs = {self.lookup_field: self.request.user.id}
        obj = get_object_or_404(queryset, **filter_kwargs)

        # May raise a permission denied
        self.check_object_permissions(self.request, obj)

        return obj

    # 24 + 3 < 50
    def create(self, request, *args, **kwargs):
        serializer: AuthSerializer = self.get_serializer(
            data=self.request.data)

        if not serializer.is_valid(raise_exception=True):
            logger.error("%s", serializer.errors)
            return Response(status=HTTP_400_BAD_REQUEST)

        if not serializer.validated_data["email"]:
            msg = {"error": "email must be"}
            return Response(msg, status=HTTP_400_BAD_REQUEST)
        # need more email validating

        self.perform_create(serializer)

        # when we call .save() password becomes hash
        username, password = (serializer.data["username"],
                              self.request.data["password"])

        user = authenticate(self.request, username=username, password=password)

        if user is not None:
            login(self.request, user)

            My_errors.tmp_context["auth_check"] = True
            return Response(My_errors.error_send(), status=HTTP_201_CREATED)

        logger.error("%s", serializer.errors)
        return Response(status=HTTP_500_INTERNAL_SERVER_ERROR)

    def authenticate(self, request, *args, **kwargs):
        error_sender = ErrorSnapshot()
        serializer: AuthSerializer = LoginSerializer(data=request.data)

        if serializer.is_valid():

            username, password = (serializer.data["username"],
                                  serializer.data["password"])

            user = authenticate(self.request,
                                username=username,
                                password=password)
            if user is not None:
                login(self.request, user)
                error_sender.set_error("auth_check")
                error_sender.set_error("is_staff", self.request.user.is_staff)
                return Response(error_sender.send(), status=HTTP_302_FOUND)

        error_sender.set_error("login_error")
        logger.error("%s", serializer.errors)
        return Response(error_sender.send(), status=HTTP_404_NOT_FOUND)

    def forgot_password(self, request, *args, **kwargs):
        # auto login not exists

        serializer = ResetPasswordSerializer(self.request.user,
                                             data=self.request.data)
        if serializer.is_valid():
            # all of it can be in update method in serializer
            msg = {"error": "wrong password"}

            if not self.request.user.check_password(
                    self.request.data.get("password")):
                return Response(msg, status=HTTP_400_BAD_REQUEST)

            self.request.user.set_password(
                self.request.data.get("new_password"))
            self.request.user.save()

            return Response(status=HTTP_205_RESET_CONTENT)

        logger.error("%s", serializer.errors)
        return Response(status=HTTP_400_BAD_REQUEST)

    def logout(self, request, *args, **kwargs):
        logout(self.request)
        return Response(status=HTTP_200_OK)


"""----LEGACY----"""


class RegistryView(APIView):
    """ Класс регистрации аккаунта с простейшей валидацией на стороне сервера """

    permission_classes = [AllowAny]

    def post(self, request):
        # Распакоука данных из сериализатора POST сессии
        error_sender = ErrorSnapshot()
        data_serialized = AuthRegisterSerializator(data=request.data)

        if not data_serialized.is_valid():
            error_sender.set_error("is_vallid_error")
            return Response(error_sender.send())

        data_serialized.save()
        username = data_serialized.data.get("username")
        password = request.data["password"]
        user = authenticate(request, username=username, password=password)
        login(request, user)
        error_sender.set_error("auth_check")
        return Response(error_sender.send())


class LoginView(APIView):
    """ Класс логина в аккаунт """

    permission_classes = [AllowAny]

    def post(self, request):
        error_sender = ErrorSnapshot()
        data_serialized = AuthSerializator(data=request.data)
        data_serialized.is_valid()
        username = data_serialized.data.get("username")
        password = data_serialized.data.get("password")
        user = authenticate(username=username, password=password)
        try:
            login(request, user)
            error_sender.set_error("auth_check")
            error_sender.set_error("is_staff", self.request.user.is_staff)
            return Response(error_sender.send())
        except AttributeError:
            # отрисовка карты, отправка ошибки на фронт
            error_sender.set_error("login_error")
            return Response(error_sender.send())


class LogoutView(APIView):
    """ Функции Копатыча | выход из аккаунта """

    def post(self, request):
        logout(request)
        return Response("")
