# Project info

> [!TIP]
> Для удобства навигации по **README** используйте раздел **Structure**

## Structure

1. [Start](#for-start-project)
2. [Important aspects](#important-aspects)

### For start project

> [!IMPORTANT]
> Проект не содержит файла настроек, поэтому:
>   1. Копируйте settings.py в папку fgeovisor/visor_bend_site.
>   2. Определите там свои учетные данные для поля DATABASES 

Для запуска проекта требуется клонировать себе его в локальный репозиторий и потом запустить .bat файл

[Top](#project-info)

> [!TIP]
> .bat файл используйте для автоматизации запуска сервера, первый раз он скачивает venv и настраивает вспомогательные файлы, потом просто запускает сервер

### Important aspects

> [!WARNING]
> Рекомендуется!
> Для баз данных не устанавливать версию PostgreSQL позже 16.4 - на нее нет PostGIS

Установщик GDAL - [OsGEO4W](https://trac.osgeo.org/osgeo4w/)

> [!TIP]
> Для входа в панель администратора нужно создать суперпользователя

[Top](#project-info)