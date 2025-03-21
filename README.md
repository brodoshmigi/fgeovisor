# Project info

> [!TIP]
> Для удобства навигации по **README** используйте раздел **Structure**

Tools used: 
1. [Django/Geodjango](https://github.com/django/django)
2. [Pystac/Pystac_client](https://github.com/stac-utils/pystac-client)
3. Google Earth Engine | Python lib | OsGEO
4. Nasa cloud storage
5. Terabox cloud storage

> [!IMPORTANT]
> Отказ от ответственности
> 
> Используемые в данном сервисе данные OpenStreetMap (OSM) предоставляются на условиях лицензии Open Database License (ODbL). Мы не несем ответственности за точность, актуальность или соответствие границ, отображаемых на картах OSM, установленным в Российской Федерации официальным границам.
>
> Отображенные границы и географическая информация носят исключительно информационный характер и не могут использоваться в качестве юридического или официального источника. Для получения точных и юридически значимых сведений о границах следует обращаться к уполномоченным государственным органам. 

## Structure

1. [Start](#for-start-project)
2. [Important aspects](#important-aspects)
3. [Test's](#test)
4. [Common errors](#common-errors)

### For start project

> [!IMPORTANT]
> Проект не содержит файла настроек, поэтому:
>   1. Копируйте settings.py в папку fgeovisor/visor_bend_site.
>   2. Определите там свои учетные данные для поля DATABASES
> 
> .bat файл используйте для автоматизации запуска сервера, первый раз он скачивает venv и настраивает вспомогательные файлы, потом просто запускает сервер

> [!WARNING]
> Для запуска проекта требуется клонировать себе его в локальный репозиторий, создать в папке nginx подпапку temp и запустить start_nginx.bat файл

[Top](#project-info)

### Important aspects

> [!WARNING]
> Рекомендуется!
> Для баз данных не устанавливать версию PostgreSQL позже 16.4 - на нее нет PostGIS

Установщик GDAL - [OsGEO4W](https://trac.osgeo.org/osgeo4w/)

PostGIS устанавливается для win через appbuilder, который по умолчанию устанавливается вместе с [PostgreSQL](https://www.postgresql.org/)

> [!TIP]
> Для входа в панель администратора нужно создать суперпользователя

[Top](#project-info)

### Test

> [!TIP]
> Для тестов создан специальный .bat файл, который запускает общие тесты по всему проекту

Тесты в проекте автоматизированы и находятся в web_interface.

Сейчас доступны только общие тесты, проверяющие корректную работу api обращений в django.
Но планируется сделать их более комплексными и важными.

[Top](#project-info)

### Common errors

> [!WARNING]
> Ошибки перечисленные ниже - самые распостраненные и на которые есть известные нам способы решения.
> Однако, даже известные способы решения могут не быть лекарством от всех проблем, которые возникнут.

1. [GDAL_ERROR 1](#gdal_error-1)
2. [The "" relation does not exist](#the-field-relation-does-not-exist)
3. [Tables doesnt create](#tables-doesnt-create)
4. [OSError: WinError 127](#winerror-127)
5. [DATABASES](#databases-error)

> [!TIP]
> Для того, чтобы ошибок возникало меньше или их не было вообще, следуйте инструкциям крайне внимательно.
>
> Это может быть утомительно, или "занимать много времени" - но, поверьте, это сэкономит вам время в будущем.
> 
[Top](#project-info)

#### GDAL_ERROR 1
> ``` python
> GDAL_ERROR 1: b'PROJ: proj_create_from_database: .\PostgreSQL\16\share\contrib\postgis-3.5\proj\proj.db
> contains DATABASE.LAYOUT.VERSION.MINOR = 2 whereas a number >= 3 is expected. It comes from another PROJ installation.'
> ```
> Возможные способы исправления этой ошибки:
> 1. Не правильный путь в venv. При создании может указаться путь на интерпретатор python находящийся в папке `OsGEO`
> 2. Версии `gdal`. Мы предусмотрели автоматическое заполнение новых версий, однако они все таки могут быть и более новые или старые. Конкретно наш - `309, 308, 310`
> 3. `PostGIS` или `PostgreSQL`. В данном пункте все расплавчато, единственные рекомендации это проверка папок `migrations` и таблиц в базе данных. При необходимости переустановите.
> 4. Проверка путей в системных `path`. Для правильной установки требуется указывать параметры в системные `path` на `gdal` и другие утилиты(внимательно читайте гайд на установку). Пути могут не перезаписаться, либо вы забыли перезапустить систему.
> 5. Возможно версии `PostGIS` и `GDAL` разные.

[Top](#project-info) |
[Back to errors list](#common-errors)

#### The field relation does not exist
> ``` python
> django.db.utils.ProgrammingError: отношение "example_db_field" не существует
> ```
> 
> или
> 
> example http request with this error
> ``` bat
> [03/Feb/2025 10:47:07] "POST /log-in/ HTTP/1.1" 200 114 Internal Server Error: /get-polygons/"
> ```
>
> Возможные способы исправления этой ошибки:
> 1. `ProgrammingError` лечится проверкой, создались ли все необходимые таблицы и имеют ли они те имена, которые запрашиваются. Для этого необходимо иметь папки `migrations` и правильный нейминг в моделях или запросе, например, сериализаторе.
> 2. Вторая ошибка менее очевидно, но они обычно идут в комплекте. Следовательно, мы сначала можем проверить нейминг в наших активных частях кода, а дальше перейти к более глубокому "корню" проекта - папки `migrations` и работа с БД.

[Top](#project-info) |
[Back to errors list](#common-errors)

#### Tables doesnt create
> Обычно эта проблема не вызывается в качестве ошибок и является причиной для появления проблемы выше.
>
> Когда делаете миграции внимательно читайте, какие таблицы были созданы - возможно, нужные вам созданы не были.
>
> Если такое произошло, способ исправить проблему(в ее самом распостраненном виде):
> 1. Убедитесь, что в каждой папке(приложении, app) лежит папка `migrations` с файлом `__init__.py`
> 2. Если они присутствуют, то проблемы находятся куда глубже, чем мы можем заглянуть.
> 3. Если они отсутствуют - создайте самостоятельно, бывает, когда django их не создает.
> 4. Проведите повторную миграцию.

[Top](#project-info) |
[Back to errors list](#common-errors)

#### WinError 127

> ``` python
> File ".\venv\Lib\site-packages\django\contrib\gis\gdal\libgdal.py", line 72, in <module>
>
>    lgdal = CDLL(lib_path)
>            ^^^^^^^^^^^^^^
>  File ".\Python312\Lib\ctypes\__init__.py", line 379, in __init__
>  
>    self._handle = _dlopen(self._name, mode)
>                   ^^^^^^^^^^^^^^^^^^^^^^^^^
>OSError: [WinError 127] Не найдена указанная процедура
>```
> Решения:
> 1. Возможно в `libgdal.py` указана версия `gdal`, которой у вас нет, хотя все остальные есть. Способ - удалить ее из списка. Например, `gdal 310` у вас нет, но `gdal 309` есть - удалите `gdal 310`

[Top](#project-info) |
[Back to errors list](#common-errors)

#### DATABASES ERROR

> ``` python
> django.core.exceptions.ImproperlyConfigured: settings.DATABASES is improperly configured.
> Please supply the NAME or OPTIONS['service'] value.
>```
> Решения:
> 1. Установите точку входа в базу данных в setting.py в корне проекта.

[Top](#project-info) |
[Back to errors list](#common-errors)
