from typing import List, Set, Generator
from functools import lru_cache
import asyncio

import pystac as stac
from pystac_client.client import Client


class SearchCatalog():

    def __init__(self, href: str = 'https://cmr.earthdata.nasa.gov/stac'):
        # href сохраняется в self.root_catalog
        self.stack_obj = stac.Link('root', href).resolve_stac_object()
        self.root_catalog = stac.Catalog.from_file(self.stack_obj)

    def __str__(self) -> str:
        return f'ID: {self.root_catalog.id},\
                \n |Title: {self.root_catalog.title}\
                \n |Desciption: {self.root_catalog.description}'

    def get_catalog(self) -> stac.Catalog:
        return self.root_catalog

    def get_search_links(self) -> Set[stac.Link]:
        return set(self.root_catalog.get_child_links())

    def get_links_titles(self) -> Generator[str, str, str]:
        for link in self.get_search_links():
            yield link.title

    # это хренота пока не работает, но думаю если setter добавить оно пойдет
    def _get_satelite_name(self):
        if type(self.satelite_names) == type([]):
            return self.satelite_names[0]
        else:
            return self.satelite_names

    def get_sort_childs(self, orderby: List[str]):
        return {
            link.get_href()
            for link in self.get_search_links() if link.title in orderby
        }


class ClientPool():
    """
    Здесь нужно будет добавить входящими аргументы.

    Но это необходимо только, если собираемся использовать более низкий уровень
    библиотеки pystac_client.
    """

    def __init__(self):
        self.clients = {}
        self._lock = asyncio.Lock()

    @lru_cache(maxsize=32)
    def get_client(self, link: str) -> Client:
        if link not in self.clients:
            self.clients[link] = Client.open(link)
        return self.clients[link]

    async def aget_client(self, link: str) -> Client:
        async with self._lock:
            if link not in self.clients:
                self.clients[link] = await asyncio.to_thread(Client.open, link)
            return self.clients[link]

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        for client in self.clients.values():
            if hasattr(client, 'close'):
                await asyncio.to_thread(client.close)
        self.clients.clear()
