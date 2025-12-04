import os
from django.contrib.gis.utils.layermapping import LayerMapping

from polygons.models import Bounds
from visor_bend_site.settings import BASE_DIR

bounds_mapping = {
    'code': 'CODE',
    'name': 'NAME',
    'geom': 'UNKNOWN',
}

bounds_geojson = BASE_DIR.parent / "Russia_GAUL_level1.geojson"

def run(verbose=True):
    lm = LayerMapping(Bounds, bounds_geojson, bounds_mapping)
    lm.save(strict=True, verbose=verbose)