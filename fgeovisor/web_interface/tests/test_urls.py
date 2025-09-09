from json import loads
from datetime import date

from django.test import TestCase
from django.contrib.auth.models import User

from images.models import UserImage
from polygons.models import UserPolygon, Bounds
from metrics.models import Metrics
"""
TestCase - нужен, если у нас происходят операции с БД (Создает тестовую БД).
SimpleTestCase - не создает тестовую БД.
Client - имитация пользователя [get, post, put, delete] для urls

В Django встроен автоматический поиск любых тестов test*.py
"""

WKT = "POLYGON((41.863781 45.117765, 42.096478 45.117765, 42.096478 44.969087, \
    41.863781 44.969087, 41.863781 45.117765))"

BDS = "POLYGON((39.5195 46.2876, 45.3642 46.2876, 45.3642 43.7804, 39.5195 43.7804, \
                39.5195 46.2876))"

TEST_METRIC = {
    "ndvi": {
        "min": 0.1,
        "max": 0.2,
        "mean": 1
    },
    "evi": {
        "min": 0.1,
        "max": 0.2,
        "mean": 1
    },
}

TEST_POLY = {
    "code": "2558",
    "type": "Feature",
    "geometry": {
        "type":
        "Polygon",
        "coordinates": [[[42.6149711781, 44.9005496272],
                         [42.8476680988, 44.9005496272],
                         [42.8476680988, 45.049405198],
                         [42.6149711781, 45.049405198],
                         [42.6149711781, 44.9005496272]]]
    },
    "properties": {}
}


class BaseUrlsTests(TestCase):
    """ Модульный тест, содержащий проверку на доступность urls и их корректную работу """

    @classmethod
    def setUpTestData(cls):
        global user, polygon_instance, metrica

        user = User.objects.create_user(username='Bombokly2',
                                        password='1X<ISRUkw+tuK')
        user.save()

        bounds = Bounds.objects.create(code=2558,
                                       name="Stavropolsky kray",
                                       geom=BDS)
        bounds.save()

        polygon_instance = UserPolygon.objects.create(owner=user,
                                                      polygon_data=WKT,
                                                      district=bounds)
        polygon_instance.save()

        metrica = Metrics.objects.create(polygon_id=polygon_instance.pk,
                                         date=date.today(),
                                         storage=TEST_METRIC)
        metrica.save()

        image_instance = UserImage.objects.create(
            polygon_id=polygon_instance,
            local_uri="./images/IMAGES/1_32MUupS.jpg",
            image_date=date.today(),
            image_index="NDVI")
        image_instance.save()

    def test_map_url_get_access_raw(self):
        response = self.client.get('')
        self.assertEqual(response.status_code, 200)
        self._valid_session_nonauth_check(response=response)

    def test_authentification_and_get_access_to_user_raw(self):
        authentificate = self.client.force_login(user=user)
        response = self.client.get('')
        self._valid_session_auth_check(response=response)

    def test_polygons_url_get_raw(self):
        authentificate = self.client.force_login(user=user)
        response = self.client.get('/crud/polygon', data={"code": 2558})
        polygon_objects = UserPolygon.objects.values('polygon_id')
        self._valid_get_polygons_data(response=response, obj=polygon_objects)

    def test_for_login_post_request_raw(self):
        # password should be raw, cause django containts only encode
        # but checking raw
        post_data = {'username': user.username, 'password': '1X<ISRUkw+tuK'}
        response = self.client.post('/log-in/', data=post_data)
        self._valid_login_check(response=response)

    def test_for_logout_post_request_raw(self):
        authentificate = self.client.force_login(user=user)
        response = self.client.post('/log-out/')
        self._valid_logout_check(response=response)

    def test_for_create_polygon_post_request_raw(self):
        authentificate = self.client.force_login(user=user)
        post_data = TEST_POLY
        response = self.client.post('/crud/polygon',
                                    data=post_data,
                                    content_type='application/json')
        self._valid_create_check(response=response)

    def test_for_delete_polygon_post_request_raw(self):
        authentificate = self.client.force_login(user=user)
        try:
            response = self.client.delete(
                f"/crud/polygon/{polygon_instance.pk}",
                content_type="application/json")
            self._valid_delete_polygons(response=response)
        except WindowsError:
            pass

    def test_for_update_polygon_post_request_raw(self):
        authentificate = self.client.force_login(user=user)
        post_data = TEST_POLY
        response = self.client.put(f'/crud/polygon/{polygon_instance.pk}',
                                   data=post_data,
                                   content_type='application/json')
        self.assertEqual(response.status_code, 200)

    def test_for_upload_img_get_request_raw(self):
        authentificate = self.client.force_login(user=user)
        response = self.client.get(
            f"/get-img?id={polygon_instance.pk}&date={date.today()}&index=NDVI",
            content_type="application/json")
        self.assertEqual(response.status_code, 302)

    def test_metrics_get(self):
        authentificate = self.client.force_login(user=user)
        response = self.client.get(
            f"/metrics?id={polygon_instance.pk}&from={date.today() - 5}&to={date.today()}"
        )
        print(response.json())
        self.assertEqual(response.json(), TEST_POLY)

    def _valid_create_check(self, response):
        self.assertEqual(response.status_code, 201)
        self.assertEqual(UserPolygon.objects.count(), 2)

    def _valid_logout_check(self, response):
        self.assertEqual(response.context, None)
        self.assertEqual(response.status_code, 200)

    def _valid_session_auth_check(self, response):
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['auth_check'])

    def _valid_session_nonauth_check(self, response):
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['auth_check'])

    def _valid_get_polygons_data(self, response, obj):
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['features'][0]['id'],
                         str(obj[0]['polygon_id']))

    def _valid_login_check(self, response):
        self.assertEqual(response.status_code, 200)
        self.assertTrue(loads(response.content)['auth_check'])

    def _valid_delete_polygons(self, response):
        self.assertEqual(response.status_code, 204)
        self.assertFalse(UserPolygon.objects.contains(polygon_instance))
