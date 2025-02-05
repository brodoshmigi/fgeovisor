from urllib3 import PoolManager
from json import dump, dumps
from typing import Dict, List, Optional, Any, Iterable
from os import path

from core.io_default_api import IODefaultAPI, terabox_hosts

DEFAULT_PARAMS = {
    'app_id': 250528,
    'web': 1,  # Detail level
    'channel': 'dubox',
    'clienttype': 0
}


class Files():

    def __init__(self):
        self._container: Dict[str, Any] = {}
        self._json: str = path.dirname(__file__) + '\\container.json'

    # Typechecking, file can be only str or obj-like
    def add_new(self,
                file: Dict[str, Any] = None,
                files: Iterable[Dict[str, Any]] | Iterable = None) -> None:
        self._container[file['server_filename']] = file

        if files:
            list(map(self.add_new, files))

    def get_files(self):
        return self._container

    def export_to_json(self):
        with open(self._json, 'w') as file:
            dump(self._container, file, indent=4)

    def save_into_BD(self):
        raise NotImplementedError('Dolbaeb')

    def dumps(self):
        return dumps(self._container, indent=4)

    def __str__(self) -> str:
        return f'len: {len(self._container)}, \nfiles: {self._container.keys()}'

    def __repr__(self) -> Dict[str, Any]:
        return {'len': len(self._container), 'files': self._container.keys()}


class CloudFileManager():

    NDUS_EXAMPLE = {'Cookie': 'ndus='}

    def __init__(self):
        self.__http = IODefaultAPI(host=terabox_hosts)
        self.container = Files()

    def file_list_web_cloud(self,
                            ndus: Dict[str, str] = NDUS_EXAMPLE,
                            dir_name: str = None):
        """ Default web-request to file list in terabox | Not openapi """
        # Keep in mind, what developers may change they api's
        fields: Dict[str, str] = {
            'order': 'time',
            'desc': 1,
            'dir': '/' if dir_name is None else dir_name,
            'num': 100,
            'page': 1,
            'showempty': 0,
        }
        fields.update(DEFAULT_PARAMS)
        response = self.__http.make_request('GET',
                                            '/api/list',
                                            token=ndus,
                                            headers={},
                                            fields=fields)
        serialized_resp: Dict = response.json()
        self._check_ndus_valid(serialized_resp)
        for ans in serialized_resp['list']:
            self.container.add_new(self._filter_dict(ans))
        self.container.export_to_json()
        return self.container

    def _filter_dict(self, dict: Dict[str, Any]) -> Dict[str, Any]:
        temp = {
            'fs_id': dict['fs_id'],
            'size': dict['size'],
            'thumbs': dict['thumbs'],
            'md5': dict['md5'],
            'server_filename': dict['server_filename'],
        }
        return temp

    def _check_ndus_valid(self, serialized_response) -> None:
        if serialized_response['errno'] != 0:
            raise ValueError('ndus is not valid')
