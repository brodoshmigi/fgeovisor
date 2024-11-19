import rest_framework.permissions as rp
from django.shortcuts import render, redirect
from django.urls import reverse
from rest_framework.views import APIView
from rest_framework.response import Response
from polygons.models import Polygon
from .models import Image
from web_interface.staff import My_errors

class UploadImg(APIView):
    """
    Функция добавления фото
    """
    permission_classes = [rp.IsAuthenticated]

    def get(self, request):
        polygon = Polygon.objects.get(polygon_id=request.data['polygon_id'])
        url = Image.objects.get(polygon=polygon).url
        return Response({'uri' : url})