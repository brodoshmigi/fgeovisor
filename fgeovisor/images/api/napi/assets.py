from typing import Generator, Any
import asyncio

import numpy as np
import pandas as pd
from pystac_client.client import Client

from abstract import Assets

class SearchAssets(Assets):

    def __init__(self, clients_pool):
        self.clients_pool = clients_pool

    # Параметры можно заменить на словарь
    def get(self, collections: pd.DataFrame,
            **kwargs) -> Generator[Any, Any, Any]:
        # -> pd.Dataframe() желательно
        # т.к. возвращать хочется больше инфы, чем просто ссылки
        # Но у нас тут еще и yield)
        true_collections = collections
        links = true_collections['href'].drop_duplicates().tolist()
        ids = true_collections['id'].tolist()
        for link in links:
            items = self._search_assets(link=link, ids=ids, **kwargs)
            data = np.array([
                item['assets']['B04']['href']
                for item in items.items_as_dicts()
            ])
            yield data

    def _search_assets(self, link: str, ids, **kwargs):
        items: Client = self.clients_pool.get_client(link=link)
        item_search = items.search(collections=ids,
                                   limit=50,
                                   query={"eo:cloud_cover": {
                                       "lt": 10
                                   }},
                                   **kwargs)
        return item_search


class ASearchAssets(Assets):
    """
    TODO
    import twisted
    """

    def __init__(self, clients_pool):
        self.clients_pool = clients_pool

    async def get(self, collections: pd.DataFrame, **kwargs):
        # -> pd.Dataframe() желательно
        # т.к. возвращать хочется больше инфы, чем просто ссылки
        # Но у нас тут еще и yield)
        true_collections = collections
        links = true_collections['href'].drop_duplicates().tolist()
        ids = true_collections['id'].tolist()

        sem = asyncio.Semaphore(10)
        all_assets = []

        async def bounded_search(link):
            async with sem:
                result = await self._search_assets(link=link,
                                                   ids=ids,
                                                   **kwargs)
                if result:
                    assets = [
                        item['assets']['B04']['href']
                        for item in result.items_as_dicts()
                    ]
                    all_assets.extend(assets)
                return result

        async with asyncio.TaskGroup() as tg:
            tasks = [
                tg.create_task(bounded_search(link=link)) for link in links
            ]
        return pd.DataFrame({'href': all_assets})

    async def _search_assets(self, link: str, ids, **kwargs):
        items: Client = self.clients_pool.get_client(link=link)
        item_search = items.search(collections=ids,
                                   limit=50,
                                   query={"eo:cloud_cover": {
                                       "lt": 10
                                   }},
                                   **kwargs)
        return item_search
