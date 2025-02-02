from typing import Dict, Optional, Tuple

from urllib3 import PoolManager, BaseHTTPResponse
from urllib.parse import urljoin

DEFAULT_HEADERS: Dict[str, str] = {'user-agent': 'python-urllib3/0.6'}


class Host():
    """ Мини тип данных для хранения двух ссылок исключительно """

    def __init__(self):
        self.__hosts: Dict[str, str] = {'PROD': None, 'DEV': None}
        self.__len: int = 0

    def reset_hosts(self):
        self.__hosts: Dict[str, str] = {}
        return self

    def add_prod_dev_hosts(self, prod_link: str, dev_link: str = None) -> None:
        if self.__len == 2:
            raise ValueError('Already have 2 hosts, change me')
        self.__hosts['PROD'] = prod_link
        self.__hosts['DEV'] = dev_link
        self.__len = 2
        return self

    def change_hosts(self, prod_link: str, dev_link: str = None) -> None:
        self.reset_hosts()
        self.__hosts['PROD'] = prod_link
        self.__hosts['DEV'] = dev_link
        return self

    def add_change_prod_host(self, link: str):
        self.__hosts['PROD'] = link
        return self

    def add_change_dev_host(self, link: str):
        self.__hosts['DEV'] = link
        return self

    def get_hosts(self) -> Dict[str, str]:
        return self.__hosts


class IODefaultAPI():
    """ Много повторяющихся параметров - имеет смысл вынести их в отдельный класс """

    def __init__(self, host: Host):
        self.__http = PoolManager()
        self.host = host.get_hosts()

    def build_url(self, endpoint: str, urltype: str = 'PROD') -> str:
        if endpoint.startswith('http'):
            return endpoint
        base_url = self.host[urltype]
        return urljoin(base_url, f'{endpoint}')

    def prepare_headers(
            self,
            token: Optional[Dict[str, str]] = None,
            headers: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """ Function for add token in headers set """
        if headers is None:
            headers = {}

        headers.update(DEFAULT_HEADERS)
        if token:
            headers.update(token)
        return headers

    def prepare_params(
            self,
            token: Optional[Dict[str, str]] = None,
            fields: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """ Function for add token in params set """
        if fields is None:
            fields = {}

        if token:
            fields.update(token)
        return fields

    def prepare(self,
                token: Optional[Dict[str, str]] = None,
                headers: Optional[Dict[str, str]] = None,
                fields: Optional[Dict[str, str]] = None,
                add_in: str = 'h',
                **kwargs):
        """ The function for unpacking args: headers, fields """
        if token is None:
            return prepared_headers, prepared_fields

        if headers and add_in == 'h' or headers == {} and add_in == 'h':
            prepared_headers = self.prepare_headers(token=token,
                                                    headers=headers)
        else:
            prepared_headers = {}

        if fields and add_in == 'q' or fields == {} and add_in == 'h':
            prepared_fields = self.prepare_params(token=token, fields=fields)
        else:
            prepared_fields = {}
        return prepared_headers, prepared_fields

    def make_request(self,
                     method: str,
                     endpoint: str,
                     token: Optional[Dict[str, str]] = None,
                     token_type: str = 'h',
                     headers: Optional[Dict[str, str]] = None,
                     fields: Optional[Dict[str, str]] = None,
                     urltype: str = 'PROD',
                     **kwargs) -> BaseHTTPResponse:
        url = self.build_url(endpoint, urltype=urltype)
        prepared_headers, prepared_fields = self.prepare(token=token,
                                                         add_in=token_type,
                                                         headers=headers,
                                                         fields=fields)
        response = self.__http.request(method=method,
                                       url=url,
                                       headers=prepared_headers,
                                       fields=prepared_fields)
        return response


nasa_hosts: Host = Host().add_prod_dev_hosts(
    prod_link='https://urs.earthdata.nasa.gov',
    dev_link='https://uat.urs.earthdata.nasa.gov')

terabox_hosts: Host = Host().add_change_prod_host(
    link='https://www.terabox.com')

#print(terabox_hosts.get_hosts())
