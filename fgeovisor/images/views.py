import rest_framework.permissions as rp
from django.shortcuts import render, redirect
from django.urls import reverse
from rest_framework.views import APIView
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from polygons.models import Polygon
from .models import Image
from web_interface.staff import My_errors

class UploadImg(APIView):
    """
    Функция добавления фото
    """
    permission_classes = [rp.IsAuthenticated]

    def post(self, request):
        if len(request.data.keys()) == 3:
            polygon = Polygon.objects.get(polygon_id=request.data['id'])
            img1 = request.data['image1']
            #img2 = request.data['image2']
            images_instance = Image(polygon=polygon, url=img1)
            images_instance.save()
            return Response({'succes': 'saved'})
        else:
            return Response({'fail': 'must 3 arguments'})
