from django.contrib import admin
from django.contrib.gis import admin
from django.contrib.gis.forms.widgets import OSMWidget
from .models import Polygon, Image, SessionStorage, ActivityLog

# Добавление моделей через декоратор, + вывод карты, если модель имеет такое поле
@admin.register(Polygon, Image)
class admin_overview(admin.GISModelAdmin):
    gis_widget = OSMWidget
    gis_widget.default_lat = 45.04
    gis_widget.default_lon = 41.97
    gis_widget.default_zoom = 15

@admin.register(SessionStorage, ActivityLog)
class admin_overview_log_and_session(admin.ModelAdmin):
    pass