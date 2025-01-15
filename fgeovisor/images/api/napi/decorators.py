import urllib3


class formater(object):
    """
    Декоратор для форматирования ответа
    """

    def __init__(self, use: bool = True):
        self.use = use

    def __call__(self, func):
        if self.use:

            def inner(*args):
                # urllib3 or requests returns dif data
                # and response may not convert to json
                returned_response: urllib3.BaseHTTPResponse = func(*args)

                if returned_response.status != 200:
                    return f'status {returned_response.status}, url={returned_response.url}'

                return self.content_check(returned_response)

            return inner
        return func

    def content_check(self, response):
        try:
            result = response.json()
        except Exception:
            result = response.data.decode()
        return result
