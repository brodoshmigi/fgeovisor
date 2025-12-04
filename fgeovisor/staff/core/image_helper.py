from os import remove

from staff.core.context.loader_context import CalculationContext
from staff.core.strategies.simple.simple_data_loader import SimpleDataLoader

from images.models import UserImage


def delete_image(polygon):
    image_instances = UserImage.objects.filter(polygon_id=polygon)
    for instance in image_instances:
        remove(str(instance.local_uri))
        instance.delete()


def update_image(context: CalculationContext, polygon):
    delete_image(polygon)

    if context is SimpleDataLoader:
        return

    new_image = context(polygon)
    new_image.visualize()
