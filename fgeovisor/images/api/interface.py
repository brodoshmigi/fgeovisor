"""
You should use interface if you want to interact with this api.

This module is designed to create a high-level interface for interacting 
with low-level classes. While you can use it directly, we recommend using 
it through the interface for better organization and maintainability.

# Important: If GDALRaster is not imported in the main file, an exception will be thrown and the program will close.
"""
from django.contrib.gis.gdal.raster.source import GDALRaster

from typing import Optional, List, Tuple, Dict
from time import perf_counter
import asyncio

import pandas as pd

from napi.auth import NasaAPIBase, NasaAPIConfig
from napi.utils import ClientPool
from napi.loader import Download, ADownload
from napi.collection import SearchCollections, ASearchCollections
from napi.assets import SearchAssets, ASearchAssets


class IDownload():

    def __init__(self, session: NasaAPIBase):
        # TODO поумнее нужно сделать
        self.base = session.session()

        self.base.create_session()
        self.session = self.base.get_session()

        self.token = session.auth.get_bearer_token()

    def download(self, url: str, name: str):
        return Download().download(session=self.session, url=url, name=name)

    def adownload(self, url_list: str):
        return ADownload().download(url_list=url_list,
                                    token=self.token)


class ICollection():

    def __init__(self,
                 satelite_names: List[str] = None,
                 catalog_list: List[str] = None,
                 clients_pool=None):
        self.args = {
            'satelite_names': satelite_names,
            'catalog_list': catalog_list,
            'clients_pool': clients_pool
        }

    def get(self, area: Tuple | List = None, date: str = None):
        return SearchCollections(**self.args).get_by_orgs(area=area, date=date)

    def aget(self, area: Tuple | List = None, date: str = None):
        return ASearchCollections(**self.args).get_by_orgs(area=area,
                                                           date=date)


class SearchEngine():

    def __init__(self, clients_pool):
        self.assets = SearchAssets(clients_pool=clients_pool)
        self.aassets = ASearchAssets(clients_pool=clients_pool)

    #SyncSearchAssets
    def get_assets(self,
                   collection: Optional[pd.DataFrame] = None,
                   date: str = None,
                   area: Tuple | List = None,
                   orderby: Dict = None,
                   max_items: int = None):
        return self.assets.get(collections=collection,
                               datetime=date,
                               bbox=area,
                               max_items=max_items)

    #AsyncSearchAssets
    def aget_assets(self,
                    collection: Optional[pd.DataFrame] = None,
                    date: str = None,
                    area: Tuple | List = None,
                    orderby: Dict = None,
                    max_items: int = None):
        return self.aassets.get(collections=collection,
                                datetime=date,
                                bbox=area,
                                max_items=max_items)


class ISearch():

    def __init__(self):
        self.clients_pool = ClientPool()

    # Нужно более глубоко здесь проработать логику стратегии
    # Чтобы просто тыкнул и все заработало
    def search_collections(self,
                           sat_names: List[str] = None,
                           catalog_filter: List[str] = None) -> ICollection:

        return ICollection(satelite_names=sat_names,
                           catalog_list=catalog_filter,
                           clients_pool=self.clients_pool)

    def search_items(self) -> SearchEngine:
        return SearchEngine(clients_pool=self.clients_pool)

    def loader(self, sauth: NasaAPIBase) -> IDownload:
        return IDownload(sauth)


def main():

    kw = {
        'area': (42.171192, 45.04739, 42.18441, 45.053151),
        'date': '2024-09/2024-11'
    }
    time1 = perf_counter()
    base = ISearch()

    api = base.search_collections(
        sat_names=['landsat', 'hlsl', 'sentinel', 'hlss'],
        catalog_filter=['USGS_LTA', 'LPDAAC_ECS', 'LPCLOUD', 'ESA'])

    dt = api.get(**kw)

    time2 = perf_counter()
    print(f'{dt}\n{time2-time1:0.4f}')

    api2 = base.search_items()

    links = api2.get_assets(collection=dt, max_items=20, **kw)

    config = NasaAPIConfig('', '')
    lbase = NasaAPIBase(config=config)

    api3 = base.loader(sauth=lbase)

    time3 = perf_counter()

    for i in links:
        print(i)
        time4 = perf_counter()
        print(f'{time4-time3:0.4f}')


async def amain():

    kw = {
        'area': (42.171192, 45.04739, 42.18441, 45.053151),
        'date': '2024-09/2024-11'
    }
    time1 = perf_counter()
    base = ISearch()

    api = base.search_collections(
        sat_names=['landsat', 'hlsl', 'sentinel', 'hlss'],
        catalog_filter=['USGS_LTA', 'LPDAAC_ECS', 'LPCLOUD', 'ESA'])

    dt = await api.aget(**kw)

    time2 = perf_counter()
    print(f'{dt}\n{time2-time1:0.4f}')

    api2 = base.search_items()

    time3 = perf_counter()
    links = await api2.aget_assets(collection=dt, max_items=5, **kw)

    time4 = perf_counter()
    print(f'{links}\n{time4-time3:0.4f}')

    user = NasaAPIConfig('', '')
    creds = NasaAPIBase(config=user)

    lof_links = links['href'].to_list()
    api3 = base.loader(sauth=creds)

    time5 = perf_counter()
    await api3.adownload(lof_links)
    time6 = perf_counter()
    print(f'{time6-time5:0.4f}')

def auth_test():
    user = NasaAPIConfig('', '')
    creds = NasaAPIBase(config=user)

    session = creds.session().create_session()

if __name__ == '__main__':
    #main()
    #asyncio.run(amain())
    auth_test()
