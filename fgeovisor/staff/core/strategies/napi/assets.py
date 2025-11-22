from typing import Generator, Any
import asyncio

import numpy as np
from pandas import DataFrame
from pystac_client.client import Client

from staff.interfaces.napi.abstract import Assets

class SearchAssets(Assets):

    def __init__(self, clients_pool):
        self.clients_pool = clients_pool

    # Параметры можно заменить на словарь
    def get(self, collections: DataFrame,
            **kwargs) -> Generator[Any, Any, Any]:
        # -> pd.Dataframe() желательно
        # т.к. возвращать хочется больше инфы, чем просто ссылки
        # Но у нас тут еще и yield)
        true_collections = collections
        links = true_collections['href'].drop_duplicates().tolist()
        ids = true_collections['id'].tolist()
        for link in links:
            items = self._search_assets(link=link, ids=ids, **kwargs)
            data = np.array([item for item in items.items_as_dicts()])
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

    async def get(self, collections: DataFrame, **kwargs):
        true_collections = collections
        links = true_collections['href'].drop_duplicates().tolist()
        ids = true_collections['id'].tolist()

        queue = asyncio.Queue()
        all_assets = []

        for link in links:
            await queue.put(link)

        async def worker():
            while True:
                link = await queue.get()
                result = await self._search_assets(link=link,
                                                   ids=ids,
                                                   **kwargs)
                if result:
                    assets = [item for item in result.items_as_dicts()]
                    all_assets.extend(assets)
                queue.task_done()
                return result

        workers = [asyncio.create_task(worker()) for _ in range(10)]
        await queue.join()

        for w in workers:
            w.cancel()
        await asyncio.gather(*workers, return_exceptions=True)

        return DataFrame({'item': all_assets})

    async def _search_assets(self, link: str, ids, **kwargs):
        items: Client = await self.clients_pool.aget_client(link=link)
        item_search = items.search(collections=ids,
                                   limit=50,
                                   query={"eo:cloud_cover": {
                                       "lt": 10
                                   }},
                                   **kwargs)
        return item_search
