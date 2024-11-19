from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from images.models import Image
from polygons.models import Polygon

"""
Тесты для приложения на проверку корректности работы. 

TestCase - нужен, если у нас происходят операции с БД (Создает тестовую БД).

SimpleTestCase - не создает тестовую БД.

Client - имитация пользователя [get, post, put, delete] для urls

В Django встроен автоматический поиск любых тестов test*.py
Поэтому нужно разбить tests на модули

Пример:

visor_bend_site\ ..
site_back\
    IMAGES\
    static\
        css\ ..
        js\ ..
    templates\
        site_back\ ..
    tests\
        __init.py # определяет tests как пакет - package, доступный по метаданным
        app_test.py
        urls_test.py
        js_test.js # Это можно вынести за пределы приложения
    __init__.py
    admin.py
    apps.py
    models.py
    serializators.py
    staff.py
    urls.py
    views.py

"""

# Создал отдельно, т.к. тесты не разбиты на отдельные файлы-модули
wkt = "POLYGON((-12.12890625 58.768200159239576, 1.1865234375 58.49369382056807, \
                5.537109375 50.2612538275847, -12.9638671875 49.18170338770662, \
                -12.12890625 58.768200159239576))"

class BaseUrlsTests(TestCase):
    """
    Модульный тест, содержащий проверку на доступность urls и их корректную работу
    """
    @classmethod
    def setUpTestData(cls):
        global user, polygon_instance
        user = User.objects.create_user(username='Bombokly2', password='1X<ISRUkw+tuK')
        user.save()
        polygon_instance = Polygon.objects.create(owner=user, polygon_data=wkt)
        polygon_instance.save()
        image_instance = Image.objects.create(polygon=polygon_instance, 
                                              url='1_32MUupS.jpg')
        image_instance.save()

    def test_map_reverse_url_get_access(self):
        response = self.client.get(reverse('map'))
        self.assertEqual(response.status_code, 200)
    
    def test_map_raw_url_get_access(self):
        response = self.client.get('')
        self.assertEqual(response.status_code, 200)

    def test_authentification_mechanism_and_get_access_to_user_reverse(self):
        authentificate = self.client.force_login(user=user)
        response = self.client.get(reverse('map'))
        self.assertEqual(response.status_code, 200)

    def test_authentification_mechanism_and_get_access_to_user_raw(self):
        authentificate = self.client.force_login(user=user)
        response = self.client.get('')
        self.assertEqual(response.status_code, 200)

    def test_polygons_url_get_reverse(self):
        authentificate = self.client.force_login(user=user)
        response = self.client.get(reverse('get-polygon'))
        self.assertEqual(response.status_code, 200)

    def test_polygons_url_get_raw(self):
        authentificate = self.client.force_login(user=user)
        response = self.client.get('/get-polygons/')
        self.assertEqual(response.status_code, 200)

    def test_for_login_post_request_reverse(self):
        post_data = {
            'username': user.username,
            'password': user.password
        }
        response = self.client.post(reverse('log-in'), data=post_data)
        self.assertEqual(response.status_code, 302)

    def test_for_login_post_request_raw(self):
        post_data = {
            'username': user.username,
            'password': user.password
        }
        response = self.client.post('/log-in/', data=post_data)
        self.assertEqual(response.status_code, 302)

    def test_for_logout_post_request_reverse(self):
        authentificate = self.client.force_login(user=user)
        response = self.client.get(reverse('log-out'))
        self.assertEqual(response.context, None)
        self.assertEqual(response.status_code, 302)

    def test_for_logout_post_request_raw(self):
        authentificate = self.client.force_login(user=user)
        response = self.client.get('/log-out/')
        self.assertEqual(response.context, None)
        self.assertEqual(response.status_code, 302)

    def test_for_create_polygon_post_request_reverse(self):
        authentificate = self.client.force_login(user=user)
        post_data = {
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[-12.1289, 58.7682], 
                                [1.1865, 58.4936],
                                [5.5371, 50.2612], 
                                [-12.9638, 49.1817],
                                [-12.1289, 58.7682]]]
            }
        }
        response = self.client.post(reverse('create-polygon'), data=post_data, 
                                    content_type='application/json')
        self.assertEqual(response.status_code, 200)

    def test_for_create_polygon_post_request_raw(self):
        authentificate = self.client.force_login(user=user)
        post_data = {
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[-12.1289, 58.7682], 
                                [1.1865, 58.4936],
                                [5.5371, 50.2612], 
                                [-12.9638, 49.1817],
                                [-12.1289, 58.7682]]]
            }
        }
        response = self.client.post('/create-polygon/', data=post_data, 
                                    content_type='application/json')
        self.assertEqual(response.status_code, 200)

    def test_for_delete_polygon_post_request_reverse(self):
        authentificate = self.client.force_login(user=user)
        post_data = {
            'id': polygon_instance.pk
            }
        response = self.client.post(reverse('delete-polygon'), data=post_data, 
                                    content_type='application/json')
        self.assertEqual(response.status_code, 200)

    def test_for_delete_polygon_post_request_raw(self):
        authentificate = self.client.force_login(user=user)
        post_data = {
            'id': polygon_instance.pk
            }
        response = self.client.post('/delete-polygon/', data=post_data, 
                                    content_type='application/json')
        self.assertEqual(response.status_code, 200)

    def test_for_update_polygon_post_request_reverse(self):
        authentificate = self.client.force_login(user=user)
        post_data = {
            "id": polygon_instance.pk,
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[-12.1289, 58.7682], 
                                [1.1865, 58.4936],
                                [5.5371, 50.2612], 
                                [-12.9638, 49.1817],
                                [-12.1289, 58.7682]]]
            }
        }
        response = self.client.post(reverse('update-poligon'), data=post_data, 
                                    content_type='application/json')
        self.assertEqual(response.status_code, 200)

    def test_for_update_polygon_post_request_raw(self):
        authentificate = self.client.force_login(user=user)
        post_data = {
            "id": polygon_instance.pk,
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[-12.1289, 58.7682], 
                                [1.1865, 58.4936],
                                [5.5371, 50.2612], 
                                [-12.9638, 49.1817],
                                [-12.1289, 58.7682]]]
            }
        }
        response = self.client.post('/update-polygon/', data=post_data, 
                                    content_type='application/json')
        self.assertEqual(response.status_code, 200)

    def test_for_upload_img_get_request_reverse(self):
        authentificate = self.client.force_login(user=user)
        response = self.client.get(reverse('get-img', kwargs={'id': polygon_instance.pk}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 200)

    def test_for_upload_img_get_request_raw(self):
        authentificate = self.client.force_login(user=user)
        response = self.client.get(f'/get-img/{polygon_instance.pk}',
                                    content_type='application/json')
        self.assertEqual(response.status_code, 200)