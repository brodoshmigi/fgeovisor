"""
Скрипт по добавлению версий gdal,
которые не добавлены стандартной реализацией geodjango
"""

import io
import os
from copy import copy

index = 0
"""
libgdal для win nt хранится в условном блоке,
поэтому мы сохранем его с двумя табуляциями,
да, обязательно удалив лишний пробле, который
появляется при первой табуляции.
"""
venv_path = os.listdir('.')
tmp_name = 'venv'
"""
Формат ввода версий гдал в функцию sample := '       ""', ''
"""
sample = ['        "gdal309"', '']
str_sample = ',        \n'.join(sample)

for path in venv_path:
    if tmp_name in path:
        path_name = path
        break
    else: 
        path_name = 'prac'

with open(f'{path_name}/Lib/site-packages/django/contrib/gis/gdal/libgdal.py',
           'r', encoding='utf-8') as FILE:
    file_data = FILE.readlines()
    new_libgdal_file = copy(file_data)

for line in file_data:
    index += 1
    if line.find('gdal302') != -1:
        break       

new_libgdal_file.insert(index, str_sample)

with open(f'{path_name}/Lib/site-packages/django/contrib/gis/gdal/libgdal.py', 
          'w', encoding='utf-8') as FILE:
    FILE.writelines(new_libgdal_file)