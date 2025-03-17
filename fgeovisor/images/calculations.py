from numpy import (seterr, ndarray, set_printoptions, nan)
from sys import maxsize
from osgeo.gdal import (Dataset, Band, Open, Warp, UseExceptions, GDT_Float32, )
from django.contrib.gis.gdal.raster.source import GDALRaster
from django.contrib.gis.gdal.raster.band import GDALBand
from matplotlib.pyplot import imsave, imshow
from copy import copy

set_printoptions(threshold=maxsize)
UseExceptions()

def calculate_NDVI(red: ndarray, nir: ndarray):
    '''
    normalization (-1, 1)
    '''
    seterr(divide='ignore', invalid='ignore')
    ndvi = (nir - red) / (nir + red)
    return ndvi

def calculate_EVI(blue: ndarray, red: ndarray, nir: ndarray,
                  L: float = 1, C1: float = 6, C2: float = 7.5, G: float = 2.5):
    '''
    normalization (0, 1)
    '''
    evi = G * (nir - red) / (nir + C1 * red - C2 * blue + L)
    return evi
    
def calculate_SAVI(red: ndarray, nir: ndarray, l: float = 0.5):
    '''
    normalization (-1, 1)
    '''
    seterr(divide='ignore', invalid='ignore')
    savi = (1 + l) * ((nir - red) / (nir + red + l))
    return savi
    
def calculate_GNDVI(green: ndarray, nir: ndarray):
    '''
    normalization (-1, 1)
    '''
    seterr(divide='ignore', invalid='ignore')
    ndre = (nir - green) / (nir + green)
    return ndre

def calculate_MSAVI(red: ndarray, nir: ndarray):
    '''
    normalization (-1, 1)
    '''
    seterr(divide='ignore', invalid='ignore')
    msavi = (1 / 2) * (2 * (nir + 1) - (((2 * nir + 1) ** 1/2 ) * 2 - 8 * (nir - red)))
    return msavi

def calculate_NDRE(red_edge: ndarray, nir: ndarray):
    '''
    normalization (-1, 1)
    '''
    seterr(divide='ignore', invalid='ignore')
    ndre = (nir - red_edge) / (nir + red_edge)
    return ndre

def crop_image(url_raster: str, geo_json, index: ndarray):
    '''
    url_raster это путь до любого из исходных растров, для получения геоданных \n
    geo_json = GeoJSONSerializer(self.polygon_object).data['geometry']
    '''
    src_ds: Dataset = Open(url_raster)
    memory_ds: Dataset = Warp('', src_ds, 
                                format='MEM', 
                                outputType=GDT_Float32, 
                                dstNodata=nan)
    src_ds.Close()

    memory_ds.WriteArray(index)
    croped_memory_ds = Warp('', memory_ds,
                         format='MEM',
                         cutlineDSName=geo_json,
                         dstNodata=nan)
    memory_ds.Close()

    croped_memory_ds_array = croped_memory_ds.ReadAsArray()
    croped_memory_ds.Close()
    return croped_memory_ds_array


