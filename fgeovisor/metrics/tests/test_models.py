from datetime import date

from django.test import TestCase
from django.contrib.auth.models import User

from images.models import UserImage
from polygons.models import UserPolygon, Bounds