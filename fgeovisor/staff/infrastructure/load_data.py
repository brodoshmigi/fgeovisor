import os
from django.contrib.gis.utils.layermapping import LayerMapping
from polygons.models import Bounds

bounds_mapping = {
    'code': 'CODE',
    'name': 'NAME',
    'geom': 'UNKNOWN',
}

bounds_geojson = os.path.abspath(os.path.join(os.path.dirname(__file__), "Russia_GAUL_level1.geojson"))

def run(verbose=True):
    lm = LayerMapping(Bounds, bounds_geojson, bounds_mapping)
    lm.save(strict=True, verbose=verbose)