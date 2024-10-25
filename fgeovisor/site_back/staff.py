from copy import copy

"""
Аналог utils.py. Тут храним вспомогательный код.
"""


class My_errors():
    '''
    самопальный обработчик ошибок

    Существует для того что бы упростить передачу ошибок с Django на js, чтобы при каждой передачи пременной 'context'
    при отрисовки html страницы не перечислять состояние все ошибок
    '''
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