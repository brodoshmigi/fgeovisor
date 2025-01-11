import time
from dataclasses import dataclass
from abc import ABC, abstractmethod
from base64 import b64encode
from typing import TypeVar, Dict, Optional, Set

import urllib3
from urllib.parse import urljoin
import requests


"""
    Реализует основную функциональность по отношению к api Nasa.
"""


_N = TypeVar('_N')

DEFAULT_HEADERS: Dict[str, str] = {'user-agent': 'python-urllib3/0.6'}

CLIENT_URL: str = 'https://urs.earthdata.nasa.gov'
DEV_URL: str = 'https://uat.urs.earthdata.nasa.gov'

CLIENT_ID: str = 'FtSFfbOeuxDcdf4px-elGw'


class formater(object):
    """
    Декоратор для форматирования ответа
    """

    def __init__(self, use: bool = True):
        self.use = use

    def __call__(self, func):
        if self.use:

            def inner(*args):
                # urllib3 or requests returns dif data
                # and response may not convert to json
                returned_response: urllib3.BaseHTTPResponse = func(*args)

                if returned_response.status != 200:
                    return f'status {returned_response.status}, url={returned_response.url}'

                return self.content_check(returned_response)

            return inner
        return func

    def content_check(self, response):
        try:
            result = response.json()
        except Exception:
            result = response.data.decode()
        return result


@dataclass
class NasaAPIConfig():
    """Фак зис булщит, это нужно где-то прятать"""
    username: str
    password: str

    # Чат гпт сказал, что это хардкорщина, типо миядзаки-like?


class NasaAuthBase(ABC):
    """
    Абстракция класса для классов аутентификации: Basic и Bearer.
    Грубо говоря, мы можем пойти в лес с топором, ножом или калашом.
    Что выберешь?

    Достаточно избыточно, но позволяет без лишних действий использовать
    Любой класс аутентификации. Плюсом можно добавить новых.
    """

    @abstractmethod
    def get_token(self) -> Dict[str, str]:
        pass

    @abstractmethod
    def reset_token(self) -> Dict[_N, _N]:
        return {}


class BasicAuth(NasaAuthBase):

    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password

    def get_token(self) -> Dict[str, str]:
        b64_creds = b64encode(
            f'{self.username}:{self.password}'.encode('utf-8'))
        return {'Authorization': f'Basic {b64_creds.decode()}'}

    def reset_token(self) -> Dict[_N, _N]:
        return super().reset_token()


class BearerAuth(NasaAuthBase):
    # TODO Фактически этому классу не хватает обращения еще на 3 URL
    # Так как токен можно получить по разному, и также его можно и удалить
    # Мы говорим сейчас не только о том, что находится в нашем классе
    # Токен находится в БД у НАСА

    def __init__(self, token: Dict[str, str]):
        self.token = token
        # Это просто рофлз, bearer токен получить можно только через обращение к api
        self.http = NasaRequestAPI()

    def get_token(self) -> Dict[str, str]:
        # TODO make request to /api/users/tokens
        # But /api/ has 2 URLs that could give a bearer token.
        # bedabeda = {'Authorization': f'Basic {self.token}'}
        self.token = self.http.make_request(
            'GET', '/api/users/tokens', self.token).json()[0]['access_token']
        return {'Authorization': f'Bearer {self.token}'}

    def reset_token(self) -> Dict[_N, _N]:
        return super().reset_token()


class AuthManager():
    """
    Используем для определения стратегии аутентификации.
    Это интерфейс, ну или он хотя бы старается делать вид, что он интерфейс.
    Можно сделать ему наследование от NasaAuthBasе, есть ли в этом смысл?
    """

    # TODO есть стратка регать класс только с кфг
    # Суть в том, что мы можем переинициализировать класс внутри себя
    # И делать мы можем это, так как basic появлятся сразу
    # То есть фактически это упростит процесс.
    # В этом случае токен станет самостоятельной единицей.
    # Его инициализацией уже будет заниматься интерпретатор,
    # А не пользователь.
    # Класc станет более абстрактным.
    # И поломать в нем что-то будет сложнее.

    def __init__(self, config: NasaAPIConfig):
        # Это не Strategy pattern, почти он.
        self.basic_token = BasicAuth(config.username,
                                     config.password).get_token()
        self.bearer_token = BearerAuth(self.basic_token).get_token()

    # Эти функции можно использовать если переопределить логику с переменной auth_strategy
    def get_basic_token(self) -> Optional[Dict[str, str]]:
        return self.basic_token

    def get_bearer_token(self) -> Optional[Dict[str, str]]:
        return self.bearer_token

    def reset_token(self) -> Optional[Dict[str, str]]:
        self.basic_token = {}
        self.bearer_token = {}


class NasaRequestAPI():

    def __init__(self):
        self.http = urllib3.PoolManager()
        self.headers: Dict[str, str] = {}

    def build_url(self, endpoint: str, utype: str = 'PROD') -> str:
        base_url = CLIENT_URL if utype == 'PROD' else DEV_URL
        if endpoint.startswith('http'):
            return endpoint
        return urljoin(base_url, f'{endpoint}')

    def prepare_headers(self,
                        token: Optional[Dict[str,
                                             str]] = None) -> Dict[str, str]:
        #
        # Тут спорный момент, .copy и инициализация пустого словаря имеет разницу 40 мс.
        headers: Dict[str, str] = {}
        headers.update(DEFAULT_HEADERS)
        if token:
            headers.update(token)
        return headers

    def make_request(self,
                     method: str,
                     endpoint: str,
                     token: Optional[Dict[str, str]] = None,
                     fields: Optional[Dict[str, str]] = None,
                     utype: str = 'PROD') -> urllib3.BaseHTTPResponse:
        #
        url = self.build_url(endpoint, utype=utype)
        headers = self.prepare_headers(token=token)
        response = self.http.request(method,
                                     url,
                                     headers=headers,
                                     fields=fields)
        return response


class NasaAPICall():

    def __init__(self, auth: AuthManager):
        # Вместо прямого наследования просто добавляем методы в класс
        self.auth = auth
        self.api = NasaRequestAPI()

    @formater(True)
    def get_oauth_profile(self, utype: str = 'PROD'):
        return self.api.make_request('GET',
                                     '/oauth/userInfo',
                                     token=self.auth.get_bearer_token(),
                                     utype=utype)

    @formater(True)
    def get_oauth_token(self):
        fields = {'grant_type': 'client_credentials'}
        return self.api.make_request('POST',
                                     '/oauth/token',
                                     token=self.auth.get_bearer_token(),
                                     fields=fields,
                                     utype='DEV')

    @formater(True)
    def get_user_id(self):
        fields = {'client_id': CLIENT_ID, 'grant_type': 'client_credentials'}
        # DI нужно будет сделать, а то беда беда
        return self.api.make_request('GET',
                                     f'/api/users/shii',
                                     token=self.auth.get_bearer_token(),
                                     fields=fields)


class NasaSessionAPI():

    def __init__(self, auth: AuthManager):
        self.auth = auth
        self.session = requests.Session()
        self.api = NasaRequestAPI()
        self.redirect_uri = 'https://data.lpdaac.earthdatacloud.nasa.gov/login'

    def create_session(self):
        fields = {
            'client_id': CLIENT_ID,
            'response_type': 'code',
            'redirect_uri': self.redirect_uri
        }
        url = self.api.build_url('/oauth/authorize')
        headers = self.api.prepare_headers(self.auth.get_basic_token())
        self.session.headers.update(headers)
        self.session.post(url=url, params=fields)

    def get_session(self):
        return self.session

    def close_session(self):
        self.session.close()
        return 'CLOSED'

    def update_cookie(self):
        pass


class NasaAPIBase():

    def __init__(self, config):
        self.auth = AuthManager(config=config)
        #self.call = NasaAPICall()
        #self.session = NasaSessionAPI()

    def request(self):
        return NasaAPICall(self.auth)

    def session(self):
        return NasaSessionAPI(self.auth)