from django.contrib.gis.gdal.raster.source import GDALRaster
from typing import List

from requests import Session

from requests import Session
from aiohttp import ClientSession
from asyncio import gather
from uuid import uuid4

from abstract import Download
from gdal_staff import tif_creator

class Download(Download):

    def download(self, **kwargs):

        http: Session = kwargs['session']

        response = http.get(url=kwargs['url'],
                            stream=True,
                            allow_redirects=True,
                            timeout=30)

        if response.status_code == 200:
            tif_creator(response.raw.data, image_name=kwargs['name'])
            return 'Complete'
        else:
            return response.status_code


class ADownload(Download):

    async def download(self,
                       url_list: List,
                       token=None,
                       cookie=None):
        async with ClientSession(headers=token, cookies=cookie) as session:
            tasks = [
                self.get_site_content(url=url, name=uuid4(), session=session)
                for url in url_list
            ]
            await gather(*tasks, return_exceptions=True)

    async def get_site_content(self, url: str, session, name: str):
        async with session.get(url) as response:
            tif_creator(await response.read(), image_name=name)