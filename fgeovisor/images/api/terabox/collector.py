from urllib3 import PoolManager
from typing import Dict, List, Optional, Any, Iterable

from core.io_default_api import IODefaultAPI, terabox_hosts

DEFAULT_PARAMS = {
    'app_id': 250528,
    'web': 1,  # Detail level
    'channel': 'dubox',
    'clienttype': 0
}


class Files():

    def __init__(self):
        self._container: List[str] = []

    # Typechecking, file can be only str or obj-like
    def add_new(self,
                file: str,
                files: Iterable[List[str]] | Iterable = None) -> None:
        self._container.append(file)

        if files:
            for f in files:
                # Dolboyeb style
                self.add_new(file=f)

    def get_files(self):
        return self._container

    def __str__(self) -> str:
        return f'len: {len(self._container)}, \nfiles: {self._container}'

    def __repr__(self) -> Dict[str, Any]:
        return {'len': len(self._container), 'files': self._container}


class CloudFileManager():

    NDUS_EXAMPLE = {'Cookie': 'ndus=YqVQEixteHuiplpSWJT9c__Cr4ZcyBRBewHKj-jp'}

    def __init__(self):
        self.__http = IODefaultAPI(host=terabox_hosts)
        self.container = Files()

    def file_list_from_cloud(self, ndus: Dict[str, str] = NDUS_EXAMPLE):
        """ Default web-request to file list in terabox | Not openapi """
        # Keep in mind, what developers may change they api's
        fields: Dict[str, str] = {
            'order': 'time',
            'desc': 1,
            'dir': '/',
            'num': 100,
            'page': 1,
            'showempty': 0,
        }
        fields.update(DEFAULT_PARAMS)
        response = self.__http.make_request('GET',
                                            '/api/list',
                                            token=ndus,
                                            fields=fields)
        serialized_resp = response.json()
        self._check_ndus_valid(serialized_resp)
        return serialized_resp

    def _check_ndus_valid(self, serialized_response) -> None:
        if serialized_response['errno'] != 0:
            raise ValueError('ndus is not valid')
