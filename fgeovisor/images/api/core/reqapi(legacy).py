from typing import Dict, Optional

from urllib3 import PoolManager, BaseHTTPResponse
from urllib.parse import urljoin

CLIENT_URL: str = 'https://urs.earthdata.nasa.gov'
DEV_URL: str = 'https://uat.urs.earthdata.nasa.gov'

DEFAULT_HEADERS: Dict[str, str] = {'user-agent': 'python-urllib3/0.6'}


class IODefaultAPI():

    def __init__(self):
        self.http = PoolManager()
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
                     utype: str = 'PROD') -> BaseHTTPResponse:
        #
        url = self.build_url(endpoint, utype=utype)
        prepared_headers = self.prepare_headers(token=token)
        response = self.http.request(method=method,
                                     url=url,
                                     headers=prepared_headers,
                                     fields=fields)
        return response
