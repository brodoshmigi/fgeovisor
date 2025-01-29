from typing import Dict, Optional, Tuple

from urllib3 import PoolManager, BaseHTTPResponse
from urllib.parse import urljoin

DEFAULT_HEADERS: Dict[str, str] = {'user-agent': 'python-urllib3/0.6'}


class Host():

    def __init__(self):
        self.__hosts: Dict[str, str] = {}

    def reset_hosts(self):
        self.__hosts: Dict[str, str] = {}
        return self

    def add_prod_dev_hosts(self, prod_link: str, dev_link: str = None) -> None:
        self.__hosts['PROD'] = prod_link
        self.__hosts['DEV'] = dev_link
        return self

    def change_hosts(self, prod_link: str, dev_link: str = None) -> None:
        self.reset_hosts()
        self.__hosts['PROD'] = prod_link
        self.__hosts['DEV'] = dev_link
        return self

    def get_hosts(self) -> Dict[str, str]:
        return self.__hosts


class IODefaultAPI():

    def __init__(self, host: Host):
        self.__http = PoolManager()
        self.host = host.get_hosts()

    def build_url(self, endpoint: str, urltype: str = 'PROD') -> str:
        if endpoint.startswith('http'):
            return endpoint
        base_url = self.host[urltype]
        return urljoin(base_url, f'{endpoint}')

    def prepare_headers(self,
                        token: Optional[Dict[str,
                                             str]] = None) -> Dict[str, str]:
        headers: Dict[str, str] = {}
        headers.update(DEFAULT_HEADERS)
        if token:
            headers.update(token)
        return headers

    def prepare_params(self, token: Optional[Dict[str, str]], fields: Optional[Dict[str, str]] = None):
        params: Dict[str, str] = {}
        params.update(fields)
        if token:
            params.update(token)
        return params

    def make_request(self,
                     method: str,
                     endpoint: str,
                     token: Optional[Dict[str, str]] = None,
                     fields: Optional[Dict[str, str]] = None,
                     urltype: str = 'PROD') -> BaseHTTPResponse:
        #
        url = self.build_url(endpoint, urltype=urltype)
        prepared_headers = self.prepare_headers(token=token)
        response = self.__http.request(method=method,
                                       url=url,
                                       headers=prepared_headers,
                                       fields=fields)
        return response


nasa_hosts: Host = Host().add_prod_dev_hosts(
    prod_link='https://urs.earthdata.nasa.gov',
    dev_link='https://uat.urs.earthdata.nasa.gov')

terabox_hosts: Host = Host().add_prod_dev_hosts(
    prod_link='https://www.terabox.com')
