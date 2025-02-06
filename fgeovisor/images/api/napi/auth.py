from dataclasses import dataclass
from base64 import b64encode
from typing import TypeVar, Dict, Optional

from requests import Session

from core.io_default_api import IODefaultAPI, nasa_hosts
from .decorators import formater
from .abstract import NasaAuthBase

_N = TypeVar('_N')

CLIENT_ID: str = 'FtSFfbOeuxDcdf4px-elGw'


@dataclass
class NasaAPIConfig():
    """Фак зис булщит, это нужно где-то прятать"""
    username: str
    password: str

    # Чат гпт сказал, что это хардкорщина, типо миядзаки-like?
    # TODO add webbrowser get creds


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
        self.http = IODefaultAPI(nasa_hosts)

    def get_token(self) -> Dict[str, str]:
        # TODO make request to /api/users/tokens
        # But /api/ has 2 URLs that could give a bearer token.
        # bedabeda = {'Authorization': f'Basic {self.token}'}
        self.token = self.http.make_request(
            'GET', '/api/users/tokens', token=self.token, headers={}).json()[0]['access_token']
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


class NasaAPICall():

    def __init__(self, auth: AuthManager):
        # Вместо прямого наследования просто добавляем методы в класс
        self.auth = auth
        self.api = IODefaultAPI(nasa_hosts)

    @formater(True)
    def get_oauth_profile(self, urltype: str = 'PROD'):
        return self.api.make_request('GET',
                                     '/oauth/userInfo',
                                     token=self.auth.get_bearer_token(),
                                     urltype=urltype)

    @formater(True)
    def get_oauth_token(self, urltype: str = 'DEV'):
        fields = {'grant_type': 'client_credentials'}
        return self.api.make_request('POST',
                                     '/oauth/token',
                                     token=self.auth.get_bearer_token(),
                                     fields=fields,
                                     urltype=urltype)

    @formater(True)
    def get_user_id(self, urltype: str = 'PROD'):
        fields = {'client_id': CLIENT_ID, 'grant_type': 'client_credentials'}
        return self.api.make_request('GET',
                                     f'/api/users/shii',
                                     token=self.auth.get_bearer_token(),
                                     fields=fields,
                                     urltype=urltype)


class NasaSessionAPI():

    def __init__(self, auth: AuthManager):
        self.auth = auth
        self.session = Session()
        self.api = IODefaultAPI(nasa_hosts)
        self.redirect_uri = 'https://data.lpdaac.earthdatacloud.nasa.gov/login'

    def create_session(self):
        fields = {
            'client_id': CLIENT_ID,
            'response_type': 'code',
            'redirect_uri': self.redirect_uri
        }
        url = [
            self.api.build_url('/oauth/authorize'),
            self.api.build_url('/profile'),
            self.api.build_url(
                'https://data.lpdaac.earthdatacloud.nasa.gov/s3credentials')
        ]
        headers = self.api.prepare_headers(self.auth.get_basic_token())
        self.session.headers.update(headers)
        self.session.get(url=url[0], params=fields)

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
