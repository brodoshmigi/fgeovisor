import logging
from datetime import date

from django.test import TestCase
from django.contrib.auth.models import User

from images.models import UserImage
from polygons.models import UserPolygon, Bounds
"""
TestCase - нужен, если у нас происходят операции с БД (Создает тестовую БД).
SimpleTestCase - не создает тестовую БД.
Client - имитация пользователя [get, post, put, delete] для urls

В Django встроен автоматический поиск любых тестов test*.py

───────────────▄▄───▐█
───▄▄▄───▄██▄──█▀───█─▄
─▄██▀█▌─██▄▄──▐█▀▄─▐█▀
▐█▀▀▌───▄▀▌─▌─█─▌──▌─▌
▌▀▄─▐──▀▄─▐▄─▐▄▐▄─▐▄─▐▄

"""

# Убрать если нужны логи с тестов
logger = logging.disable()

wkt = "POLYGON((-12.12890625 58.768200159239576, 1.1865234375 58.49369382056807, \
                5.537109375 50.2612538275847, -12.9638671875 49.18170338770662, \
                -12.12890625 58.768200159239576))"

bds = "POLYGON((39.5195 46.2876, 45.3642 46.2876, 45.3642 43.7804, 39.5195 43.7804, \
                39.5195 46.2876))"


class BaseModelsTests(TestCase):
    """
    Каждый созданный тест независим, объявить глобальные(я е) данные можно только в:
    setUpTestData и setUp при помощи self.
    setUp активируется всегда при запуске любого теста
    """

    @classmethod
    def setUpTestData(cls):
        # Эти подозрительные типы похоже уже разнюхали, что я недавно вылечился от паранойи.
        global user, bounds

        user = User.objects.create_user(username="Bombokly", password="123456")

        bounds = Bounds.objects.create(code=2558,
                                       name="Stavropolsky kray",
                                       geom=bds)

        # print(bounds.id)

    def test_polygon_create(self):
        self.assertEqual("Bombokly", user.username)

        UserPolygon.objects.create(owner=user,
                                   polygon_data=wkt,
                                   district=bounds)

        self.assertTrue(UserPolygon.objects.exists())

    def test_image_create(self):
        UserPolygon.objects.create(owner=user,
                                   polygon_data=wkt,
                                   district=bounds)

        polygon_instance = UserPolygon.objects.get(owner=user)

        UserImage.objects.create(polygon_id=polygon_instance,
                                 local_uri="./IMAGES/unnamed.jpg",
                                 image_date=date.today(),
                                 image_index="NDVI")
        self.assertTrue(UserPolygon.objects.exists())

    """
    def test_email_validation_check(self):
        user_instance = User.objects.create_user(username='Bobma', email='12345', 
                                                 password='123456')
        self.assertTrue('@' in user_instance.email, msg='User created with nonvalid email')
    """


class SerializerTests(TestCase):
    """
    █▀▀░█░█░█▀█░█▀▀░█▀█░░
    ▀▀█░█░█░█▀▀░█▀░░█▀▄░░
    ▀▀▀░▀▀▀░▀░░░▀▀▀░▀░▀░░
    █▄░▄█░█▀▀░█▀▀▀░ █▀█░░░
    █░█░█░█▀░░█░▀█░█▀▀█░░
    ▀░▀░▀░▀▀▀░▀▀▀▀░▀░░▀░░
    █░░█░█░▀▀█▀▀░█▀█░ █▀█░
    █░░█░█░░░█░░░█▀▄░█▀▀█
    ▀▀▀▀░▀▀▀░▀░░░▀░▀░▀░░▀
    ░░░░█▀▀░█▀█░█░█▀▀░░░░
    ░░░░█▀░░█▀▀░█░█░░░░░░
    ░░░░▀▀▀░▀░░░▀░▀▀▀░░░░
    ░░░█░░░█▀█░█▀▀░█▀█░░░
    ░▀▀█▀▀░█▀▄░█▀░░█▀▀░░░
    ░░░█░░░▀░▀░▀▀▀░▀░░░░░
    """

    @classmethod
    def setUpTestData(cls):
        return super().setUpTestData()
