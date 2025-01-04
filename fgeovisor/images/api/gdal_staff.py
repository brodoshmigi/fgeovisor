from django.contrib.gis.gdal.raster.source import GDALRaster

"""
    Модуль для интерпретации gdal под наши нужды.
    Т.е. отсюда тянем gdal.
"""

def gdal_rast_handler(*args: str, image_name: str) -> GDALRaster:
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
    
    return raster_create
