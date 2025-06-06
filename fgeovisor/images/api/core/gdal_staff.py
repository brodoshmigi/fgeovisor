from django.contrib.gis.gdal.raster.source import GDALRaster
from matplotlib.pyplot import (imshow, imsave)
from matplotlib import use

"""
    Модуль для интерпретации gdal под наши нужды.
    Т.е. отсюда тянем gdal.
"""

def tif_creator(*args: str, image_name: str) -> GDALRaster:
    """
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
