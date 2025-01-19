from django.contrib.gis.gdal.raster.source import GDALRaster

from requests import Session

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

    def download(self, **kwargs):
        pass