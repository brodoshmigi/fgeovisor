from copy import copy
"""
Аналог utils.py. Тут храним вспомогательный код.
"""


class My_errors():
    """
    Cамопальный обработчик ошибок

    Существует для того что бы упростить передачу ошибок с Django на js, 
    При каждой передачи пременной 'context' при отрисовки html страницы 
    Не перечислять состояние всех ошибок
    """
    #список всех существующих ошибок
    error_wordbook = {
        'auth_check': False,
        'is_staff': False,
        'is_vallid_error': False,
        'login_error': False,
        'create_error': False,
        'photo': False
    }

    tmp_context = copy(error_wordbook)

    def error_send():
        final = copy(My_errors.tmp_context)
        #сбрасывает временную переменную
        My_errors.tmp_context = copy(My_errors.error_wordbook)
        return (final)


def is_query_valid(query_dict, q_equals) -> bool:
    query_len = len(query_dict.keys())

    if query_len < 3 or query_len > 3:
        return False

    if q_equals != set():
        return False

    return True
