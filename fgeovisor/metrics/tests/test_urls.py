from json import loads
from datetime import date

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

from images.models import UserImage
from polygons.models import UserPolygon, Bounds
from metrics.models import Metrics