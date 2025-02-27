from django.urls import path, re_path

from . import views

crud_poly_rest = [
    re_path(r'^crud/polygon$',
            views.Polygons.as_view({
                'get': 'list',
                'post': 'create',
            }),
            name='cr-for-poly'),
    re_path(
        r'^crud/polygon/(?P<pk>[0-9a-f-]{34,36})$',
        views.Polygons.as_view({
            'delete': 'destroy',
            # Можно убрать и оставить просто post
            # у put логика с проверкой и если полигона нет - создаст новый
            'put': 'update'
        }),
        name='ud-for-poly')
]

v1_rest_view = [
    # ?id=id
    re_path(r'^v1/polygon', views.PolygonsView.as_view(), name='v1-poly'),
]

urlpatterns = []

urlpatterns += crud_poly_rest
urlpatterns += v1_rest_view
