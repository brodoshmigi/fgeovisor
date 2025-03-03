from numpy import (seterr, ndarray)
from osgeo import gdal, ogr
from osgeo.gdal import Dataset


gdal.UseExceptions()

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

def crop_image(tiff: str, polygon):
    gdal.Warp(r'E:\GEO_DJAMBO\geodjangorainmarker\output_raster.png', tiff,
              format="png",
              cutlineDSName=r'E:\GEO_DJAMBO\geodjangorainmarker\fgeovisor\images\IMAGES\cutline.geojson',
              srcNodata=1)

