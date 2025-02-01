# Project info

> [!TIP]
> Для удобства навигации по **README** используйте раздел **Structure**

## Structure

1. [Start](#for-start-project)
2. [Important aspects](#important-aspects)
3. [Test's](#test-cases)

### For start project

> [!IMPORTANT]
> Проект не содержит файла настроек, поэтому:
>   1. Копируйте settings.py в папку fgeovisor/visor_bend_site.
>   2. Определите там свои учетные данные для поля DATABASES
> 
> .bat файл используйте для автоматизации запуска сервера, первый раз он скачивает venv и настраивает вспомогательные файлы, потом просто запускает сервер

> [!WARNING]
> Для запуска проекта требуется клонировать себе его в локальный репозиторий и потом запустить .bat файл

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

### Test сases

> [!TIP]
> Для тестов создан специальный .bat файл, который запускает общие тесты по всему проекту

Тесты в проекте автоматизированы и находятся в web_interface.

Сейчас доступны только общие тесты, проверяющие корректную работу api обращений в django.
Но планируется сделать их более комплексными и важными.

[Top](#project-info)
