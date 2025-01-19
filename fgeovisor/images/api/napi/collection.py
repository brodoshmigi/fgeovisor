from typing import List, Tuple
import asyncio

import pandas as pd
from pystac_client.client import Client

from utils import SearchCatalog
from abstract import Collections

class SearchCollections():

    def __init__(self,
                 satelite_names: List[str] = ['landsat'],
                 catalog_list: List[str] = None,
                 clients_pool=None):
        self.satelite_names = set(satelite_names)
        self.catalog = SearchCatalog().get_sort_childs(orderby=catalog_list)
        self.clients_pool = clients_pool

    def get_by_orgs(self,
                    area: Tuple | List = None,
                    date: str = None) -> pd.DataFrame:
        true_collections = pd.DataFrame()
        for link in self.catalog:
            data = pd.DataFrame([{
                'id': c['id'],
                'href': link
            } for c in self._search_collection(
                link=link, bbox=area, datetime=date)])
            filtered = data[data['id'].str.lower().apply(
                lambda x: any(search in x for search in self.satelite_names))]
            true_collections = pd.concat([true_collections, filtered])
        return true_collections

    async def aget_by_orgs(self,
                           area: Tuple | List = None,
                           date: str = None) -> pd.DataFrame:
        queue = asyncio.Queue()
        _lock = asyncio.Lock()
        sem = asyncio.Semaphore(10)
        true_collections = []

        for link in self.catalog:
            await queue.put(link)

        async def worker():
            while True:
                link = await queue.get()
                async with sem:
                    collections = await self._asearch_collection(link=link,
                                                                 bbox=area,
                                                                 datetime=date)
                    filtered_collections = [
                        {'id': c['id'], 'href': link}
                        for c in collections.collections_as_dicts()
                        if any(search in c['id'].lower() 
                             for search in self.satelite_names)
                    ]
                    async with _lock:
                        true_collections.extend(filtered_collections)
                queue.task_done()

        workers = [
            asyncio.create_task(worker())
            for _ in range(min(32, len(self.catalog)))
        ]
        await queue.join()

        for w in workers:
            w.cancel()
        await asyncio.gather(*workers, return_exceptions=True)

        return pd.DataFrame(true_collections)

    def get_by_links(self):
        for link in self.catalog:
            return self._get_collections(link=link)

    def _search_collection(self, link: str, **kwargs):
        client: Client = self.clients_pool.get_client(link=link)
        collections = client.collection_search(q='landsat', **kwargs)
        return collections.collections_as_dicts()

    async def _asearch_collection(self, link: str, **kwargs):
        client: Client = self.clients_pool.get_client(link=link)
        collections = client.collection_search(q='landsat', **kwargs)
        return collections

    def _get_collections(self, link: str):
        # Маленький шаг для человека, но огромный для меня
        # Большее понимание библиотеки находится здесь...
        client: Client = self.clients_pool.get_client(link=link)
        result = pd.DataFrame([{
            'r': c.id,
            'link': link,
        } for c in client.get_collections()])
        return result.drop_duplicates()

    def _get_collection(self, link: str, id: str):
        client: Client = self.clients_pool.get_client(link=link)
        result = pd.DataFrame([{
            'r': c.id,
            'link': link,
        } for c in client.get_collection(id)])
        return result