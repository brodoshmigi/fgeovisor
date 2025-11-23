from os import remove, rmdir
from sys import maxsize
from numpy import (seterr, ndarray, set_printoptions, nan)

from osgeo.gdal import (
    Dataset,
    Open,
    Warp,
    UseExceptions,
    GDT_Float64,
)
from django.contrib.gis.gdal.raster.source import GDALRaster

from json import dump

from pathlib import Path

from matplotlib.pyplot import (imshow, imsave)
from matplotlib import use

set_printoptions(threshold=maxsize)
UseExceptions()

# Все расчеты индексов нужно по хорошему делить на 10000 тысяч, это просто так, заметка

def calculate_NDVI(red: ndarray, nir: ndarray):
    '''normalization (-1, 1)'''
    #seterr(divide='ignore', invalid='ignore')
    ndvi = (nir - red) / (nir + red)
    ndvi = ndvi.round(2)
    return ndvi


def calculate_EVI(blue: ndarray,
                  red: ndarray,
                  nir: ndarray,
                  L: float = 1,
                  C1: float = 6,
                  C2: float = 7.5,
                  G: float = 2.5):
    '''normalization (0, 1)'''
    evi = G * (nir - red) / (nir + C1 * red - C2 * blue + L)
    return evi


def calculate_SAVI(red: ndarray, nir: ndarray, l: float = 0.5):
    '''normalization (-1, 1)'''
    #seterr(divide='ignore', invalid='ignore')
    savi = (1 + l) * ((nir - red) / (nir + red + l))
    return savi


def calculate_GNDVI(green: ndarray, nir: ndarray):
    '''normalization (-1, 1)'''
    #seterr(divide='ignore', invalid='ignore')
    ndre = (nir - green) / (nir + green)
    return ndre


def calculate_MSAVI(red: ndarray, nir: ndarray):
    '''normalization (-1, 1)'''
    #seterr(divide='ignore', invalid='ignore')
    msavi = (1 / 2) * (2 * (nir + 1) - (((2 * nir + 1)**1 / 2) * 2 - 8 *
                                        (nir - red)))
    return msavi


def calculate_NDRE(red_edge: ndarray, nir: ndarray):
    '''normalization (-1, 1)'''
    #seterr(divide='ignore', invalid='ignore')
    ndre = (nir - red_edge) / (nir + red_edge)
    return ndre


def crop_image(url_raster: str, geo_json, index: ndarray):
    '''
    url_raster это путь до любого из исходных растров, для получения геоданных \n
    geo_json = GeoJSONSerializer(self.polygon_object).data['geometry']
    '''
    src_ds: Dataset = Open(url_raster)
    memory_ds: Dataset = Warp('',
                              src_ds,
                              format='MEM',
                              outputType=GDT_Float64,
                              dstNodata=nan)
    src_ds.Close()

    memory_ds.WriteArray(index)
    croped_memory_ds = Warp('',
                            memory_ds,
                            format='MEM',
                            cutlineDSName=geo_json,
                            dstNodata=nan)
    memory_ds.Close()

    croped_memory_ds_array = croped_memory_ds.ReadAsArray()
    croped_memory_ds.Close()
    return croped_memory_ds_array

def tif_creator(*args: str, image_name: str) -> GDALRaster:
    """ ---Legacy---
    Создает .tif файл из виртуальных .tif файлов

    Или может создать один .tif с несколькими каналами из нескольких .tif с одним каналом

    Args:
        *args (str):
            Принмает в себя ссылки на .tif файл.
        image_name (str):
            Задает имя снимку исходя из даты его создания
    Returns:
        Image (byte or .tif):
            Возвращает созданный/объединенный .tif новым файлов
            и в течении сессии сохраняется в оперативной памяти.
    """
    if not args:
        raise ValueError('At least one .tif file is required.')

    img_list_handler = [GDALRaster(value) for value in args]

    source = img_list_handler[0]
    source_driver = source.driver

    # в name указывается имя директории, в которую сохранится файл
    raster_create = GDALRaster(
        {
            'srid': source.srid,
            'width': source.width,
            'height': source.height,
            'driver': str(source_driver),
            'name': f'{str(image_name)}.tif',
            'datatype': source.bands[0].datatype(),
            'nr_of_bands': len(img_list_handler),
        }
    )

    for y in range(len(img_list_handler)):
        raster_create.bands[y].data(img_list_handler[y].bands[0].data())
    
    #return raster_create

def jpeg_creator(*args: str, image_name: str) -> GDALRaster:

    if not args:
        raise ValueError('At least one .tif file is required.')

    img_list_handler = [GDALRaster(value) for value in args]

    source = img_list_handler[0]
    source_driver = source.driver

    # в name указывается имя директории, в которую сохранится файл
    raster_create = GDALRaster(
        {
            'name': f'/vsimem/{image_name}',
            'srid': source.srid,
            'width': source.width,
            'height': source.height,
            'driver': str(source_driver),
            'datatype': source.bands[0].datatype(),
            'nr_of_bands': len(img_list_handler),
        }
    )

    for y in range(len(img_list_handler)):
        raster_create.bands[y].data(img_list_handler[y].bands[0].data())

    matplot_helper(image_name=image_name, pixel_array=raster_create.bands[0].data())

def matplot_helper(image_name: str, pixel_array):
    use('agg')
    valid_array = imshow(pixel_array).get_array()
    imsave((f'C:/Users/123/Desktop/{image_name}.jpg'), valid_array, cmap='Grey')

def read_bands(dir_path: Path) -> list[GDALRaster]:
        list_of_rasters = [f for f in dir_path.iterdir() if f.is_file()]
        bands = [
            GDALRaster(fp).bands[0].data().astype("float64")
            for fp in list_of_rasters
        ]
        return bands

def remove_bands(dir_path: Path) -> None:
        list_of_rasters = [f for f in dir_path.iterdir() if f.is_file()]
        [remove(fp) for fp in list_of_rasters]
        rmdir(dir_path)