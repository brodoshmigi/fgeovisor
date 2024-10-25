from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Polygon, Image, SessionStorage, ActivityLog
from django.contrib.auth import login, authenticate
from copy import copy

"""
Тут храним сериализаторы данных из quaryset моделей, который в БД у нас
Сериализаторы делают каткаткат и выдают нам красивые гейсоны
Эти json мы будем использовать во вьюхах, переадресовывая все в fetch на форнте ммм сладко
"""

# Получает queryset из модели Polygon
class PolygonSerializator(serializers.ModelSerializer):

    class Meta:
        model = Polygon
        fields = '__all__'

# Получает queryset из модели Image
class ImageSerializator(serializers.ModelSerializer):

    class Meta:
        model = Image
        fields = '__all__'



#### Основной сериализатор с связми User + полигон + изображение
class PolygonOwnerSerializator(serializers.ModelSerializer):

    # 
    Images = ImageSerializator(many=True, read_only=True, source='images')
    
    # Обращается в модель Polygon к записи Login и оттуда берет через связь username
    login_username = serializers.ReadOnlyField(source="login.username")

    class Meta:
        model = Polygon
        fields = ['login', 'login_username', 'polygon_id', 'polygon_data', 
                    'Images', 'created_at', 'updated_at']
        

"""
Сериализатор для регистрации бим бим бам бам
"""

class UserRegistrationSerializator(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ["username", "email", "password"]
        #extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        """
        Хэширование пароля, т.к. django самостоятельно этого на уровне модели
        не умеет, точнее хэширование может быть только в процессах
        """
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user 

###Сериализатор для логина буп буп биб бам
class UserLoginSerializator(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ["username", "password"]
        
        #extra_kwargs = {'password': {'read_only': True}}
    
'''
самопальный обработчик ошибок
'''
class My_errors():

    error_wordbook={
            'auth_check': False,
            'is_staff': False,
            'is_vallid_error': False,
            'login_error': False,
            }
    
    tmp_context = copy(error_wordbook)
    
    def error_send():
        final = copy(My_errors.tmp_context)
        My_errors.tmp_context = copy(My_errors.error_wordbook)
        return(final)
    