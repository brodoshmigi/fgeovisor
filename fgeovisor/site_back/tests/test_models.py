from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from site_back.models import Polygon, Image


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

class BaseModelsTests(TestCase):
    """
    Модульный тест, содержащий в себе функциональные на проверку работы функций.
    Каждый созданный тест независим, объявить глобальные данные можно только в:
    setUpTestData и setUp при помощи self.
    setUp активируется всегда при запуске любого теста
    """
    @classmethod
    def setUpTestData(cls):
        # Создаем пользователя
        User.objects.create_user(username='Bombokly', password='123456')
        # чтобы каждый раз их не поднимать при тестах, объявил как глобал
        global user
        user = User.objects.get(id=1)
          
    def test_polygon_create(self):
        # Создаем полигон и проверяем на ошибку с моделью User
        self.assertEqual('Bombokly', user.username)
        Polygon.objects.create(owner=user, polygon_data=wkt)
        # Если нельзя будет получить, выдаст ошибку
        self.assertTrue(Polygon.objects.all())
        
    def test_image_create(self):
        # Создаем изображение
        Polygon.objects.create(owner=user, polygon_data=wkt)
        polygon_instance = Polygon.objects.get(owner=user)
        Image.objects.create(polygon=polygon_instance, url='./IMAGES/unnamed.jpg')
        # Если нельзя будет получить, выдаст ошибку
        self.assertTrue(Image.objects.all())
    
    """
    def test_email_validation_check(self):
        # Проверяем, можно ли сохранить в БД какашку
        # Однако, мы сохраняем пользователя через rest_framework
        # Значит нам все равно, он провалидирует за нас
        user_instance = User.objects.create_user(username='Bobma', email='12345', 
                                                 password='123456')
        self.assertTrue('@' in user_instance.email, msg='User created with nonvalid email')
    """