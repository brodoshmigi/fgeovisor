from django.contrib import admin
from django.contrib.gis import admin
from django.contrib.gis.forms.widgets import OSMWidget

from polygons.models import UserPolygon, ImageBounds, Bounds
from images.models import UserImage, NasaImage
from .models import SessionStorage, ActivityLog


@admin.register(UserPolygon, ImageBounds, UserImage, NasaImage, Bounds)
class admin_overview(admin.GISModelAdmin):
    gis_widget = OSMWidget
    gis_widget.default_lat = 45.04
    gis_widget.default_lon = 41.97
    gis_widget.default_zoom = 15


@admin.register(SessionStorage, ActivityLog)
class admin_overview_log_and_session(admin.ModelAdmin):
    pass
