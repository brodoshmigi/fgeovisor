from django.contrib.auth.models import User

from rest_framework import serializers


class AuthRegisterSerializator(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ["username", "email", "password"]
        #write_only = True

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class AuthSerializator(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ["username", "password"]
        #read_only = True

class AuthSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = '__all__'
        extra_kwargs = {
            'username': {'required': True, 'allow_blank': False},
            'password': {'required': True, 'allow_blank': False},
            'email': {'required': True, 'allow_blank': True}
        }
