from copy import copy
from .models import Polygon
from .serializators import PolygonFromDbSerializer
from PIL import Image

"""
Аналог utils.py. Тут храним вспомогательный код.
"""

class My_errors():
    """
    Cамопальный обработчик ошибок

    Существует для того что бы упростить передачу ошибок с Django на js, чтобы при каждой передачи пременной 'context'
    при отрисовки html страницы не перечислять состояние все ошибок
    """
    #список всех существующих ошибок
    error_wordbook={
            'auth_check': False,
            'is_staff': False,
            'is_vallid_error': False,
            'login_error': False,
            'create_error': False,
            }
    
    tmp_context = copy(error_wordbook)
    
    def error_send():
        final = copy(My_errors.tmp_context)
        #сбрасывает временную переменную 
        My_errors.tmp_context = copy(My_errors.error_wordbook) 
        return(final)


def get_polygons(user_id):
        """
        Отправляем запрос в БД, формируем список из пользовательских полигонов
        """
        polygons = Polygon.objects.filter(owner=user_id)
        tmp = []
        for objects in polygons: 
            tmp.append(PolygonFromDbSerializer(objects).data)
        return tmp