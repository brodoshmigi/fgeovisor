from os import path

from json import dump, dumps, loads
from re import compile, search
from json.decoder import JSONDecodeError
from typing import Dict, Any, Iterable

from core.io_default_api import IODefaultAPI, terabox_hosts
from .utils import create_sign

DEFAULT_PARAMS = {
    'app_id': 250528,
    'web': 1,  # Detail level
    'channel': 'dubox',
    'clienttype': 0
}

TERABOX_ERRNO = {
    '2': 'one of params is incorrect',
    '113': 'timestamp is incorrect'
}

class Files():

    def __init__(self):
        self._container: Dict[str, Any] = {}
        self._json: str = path.dirname(__file__) + '\\container.json'

    def add_new(self,
                file: Dict[str, Any] = None,
                files: Iterable[Dict[str, Any]] | Iterable = None) -> None:
        self._container[file['server_filename']] = file

        if files:
            list(map(self.add_new, files))

    def get_files(self):
        return self._container

    def export_json(self):
        with open(self._json, 'w') as file:
            dump(self._container, file, indent=4)

    def save_into_BD(self):
        raise NotImplementedError('Dolbaeb')

    def dumps(self):
        return dumps(self._container, indent=4)

    def null_check(self) -> bool:
        return not self._container

    def fs_ids(self):
        """ fs_ids need for get_download_urls """
        for key in self._container:
            yield self._container[key]['fs_id']

    def __str__(self) -> str:
        return f'len: {len(self._container)}, \nfiles:\n {', '.join(self._container.keys())}'

    def __repr__(self) -> Dict[str, Any]:
        return {'len': len(self._container), 'files': self._container.keys()}


class CloudFileManager():

    NDUS_EXAMPLE = {'Cookie': 'ndus='}

    def __init__(self, container: Files, ndus: Dict[str, str] = NDUS_EXAMPLE):
        self.__http = IODefaultAPI(host=terabox_hosts)
        self.container = container
        self.ndus = ndus
        # tokens = self.get_tokens()
        # self.tokens = {
        #   'csrfToken': tokens['csrf']
        #   'jsToken': tokens['jsToken']
        #   'bdstoken': tokens['bdstoken']
        # }

    def file_cloud_repr(
            self,
            # ndus: Dict[str, str] = NDUS_EXAMPLE,
            order: str = 'time',
            desc: int = 0,
            num: int = 100,
            page: int = 1,
            dir_name: str = '/',
            export_json: bool = True) -> Files:
        """ Default web-request to file list in terabox | Not openapi """
        # Keep in mind, what developers may change they api's
        self.get_info()

        fields: Dict[str, Any] = {
            'order': order,
            'desc': desc,
            'dir': dir_name,
            'num': num,
            'page': page,
            'showempty': 0,
        }
        fields.update(DEFAULT_PARAMS)

        response = self.__http.make_request('GET',
                                            '/api/list',
                                            token=self.ndus,
                                            fields=fields)
        serialized_resp: Dict = response.json()

        for ans in serialized_resp['list']:
            self.container.add_new(self._filter_dict(ans))

        # Useful in some situations, example, noSQL or local save, debug
        if export_json:
            self.container.export_json()

        return self.container

    def get_download_urls(
            self,
            # ndus: Dict[str, str] = NDUS_EXAMPLE,
            fid: int = None):
        """ 
        Sign and bdstoken are automatically generated by the browser, 
        so you cannot get them from Python. (but we can)
        """
        take_sign = self.get_info(True)
        s1, s2, timestamp = take_sign['data']['sign3'], take_sign['data'][
            'sign1'], take_sign['data']['timestamp']

        if self.container.null_check() and fid is None:
            raise ValueError('Cant find file for download | Files is empty')
        
        if fid:
            files_list = [fid]
        else:
            files_list = [_fid for _fid in self.container.fs_ids()]

        fields: Dict[str, Any] = {
            'fidlist': files_list,
            'type': 'dlink',
            'vip': 2,
            'sign': create_sign(s1, s2),
            'timestamp': timestamp,
            'need_speed': 0,
        }
        fields.update(DEFAULT_PARAMS)
        
        response = self.__http.make_request('GET',
                                            '/api/download',
                                            token=self.ndus,
                                            fields=fields)
        serialized_resp: Dict = response.json()

        return serialized_resp

    def get_info(
            self,
            # ndus: Dict[str, str] = NDUS_EXAMPLE,
            response_out: bool = False):
        """ need js interpretator for use this correct """
        response = self.__http.make_request('GET',
                                            '/api/home/info',
                                            token=self.ndus)

        try:
            serialized_resp: Dict = response.json()

            if response_out:
                return serialized_resp

            del serialized_resp
        except JSONDecodeError:
            raise ValueError('ndus in not valid')

    def get_tokens(self) -> str:
        """ makes a params dict """
        response = self.__http.make_request('GET', '/main', token=self.ndus)
        tdata_regex = compile(r'<script>var templateData = (.*);</script>')
        mach = tdata_regex.search(response.data.decode())
        tdata = loads(mach.group(1)) if mach else {}

        if tdata['jsToken']:
            tdata['jsToken'] = search(r'%28%22(.*)%22%29',
                                      tdata['jsToken']).group(1)

        return tdata

    def _filter_dict(self, fdict: Dict[str, Any]) -> Dict[str, Any]:
        temp = {
            'fs_id': fdict['fs_id'],
            'size': fdict['size'],
            'thumbs': fdict['thumbs'],
            'md5': fdict['md5'],
            'server_filename': fdict['server_filename'],
        }
        return temp
