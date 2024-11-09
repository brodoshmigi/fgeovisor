from rest_framework import serializers
from django.contrib.auth.models import User
from .models import SessionStorage, ActivityLog
from rest_framework_gis.serializers import GeoFeatureModelSerializer


"""
Тут храним сериализаторы данных из quaryset моделей, который в БД у нас
Сериализаторы делают каткаткат и выдают нам красивые гейсоны
Эти json мы будем использовать во вьюхах, переадресовывая все в fetch на форнте ммм сладко
"""

class UserRegistrationSerializator(serializers.ModelSerializer):
    """
    Сериализатор для регистрации бим бим бам бам
    """
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

class UserLoginSerializator(serializers.ModelSerializer):
    """
    Сериализатор для логина буп буп биб бам
    """
    class Meta:
        model = User
        fields = ["username", "password"]
        
        #extra_kwargs = {'password': {'read_only': True}}
    
    