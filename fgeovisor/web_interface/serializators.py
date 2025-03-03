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
            'username': {
                'required': True,
                'allow_blank': False
            },
            'password': {
                'required': True,
                'allow_blank': False
            },
            'email': {
                'required': True,
                'allow_blank': True
            },
            # Мне это не нравится)
            'is_staff': {
                'read_only': True
            },
            'is_active': {
                'read_only': True
            },
            'date_joined': {
                'read_only': True
            },
            'groups': {
                'read_only': True
            },
            'user_permissions': {
                'read_only': True
            },
            'is_superuser': {
                'read_only': True
            },
            'last_login': {
                'read_only': True
            }
        }

class ResetPassword(serializers.ModelSerializer):

    password = serializers.CharField(source='user.password', style={'input_type': 'password'},
        max_length=20, min_length=4)
    new_password = serializers.CharField(style={'input_type': 'password'},
        max_length=20, min_length=4)

    class Meta:
        model = User
        fields = ('password', 'new_password')
