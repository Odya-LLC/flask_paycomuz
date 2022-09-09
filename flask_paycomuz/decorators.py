from flask import request
import base64
from .errors import PaycomErrors

p_errors = PaycomErrors()

def base64ToString(b):
    return base64.b64decode(b).decode('utf-8')


def authorize(key):
    def decorator_function(original_function):
        def wrapper_function(*args, **kwargs):
            res = request.get_json()
            _id = res['id']
            if not 'Authorization' in request.headers:
                return p_errors.Unauthorized(_id)
            data = request.headers['Authorization']
            token = str.replace(str(data), 'Basic ','')
            data = base64ToString(token).split(":")
            if len(data) != 2:
                return p_errors.Unauthorized(_id)
            login, password = data
            if password != key:
                return p_errors.Unauthorized(_id)
            result = original_function(*args, **kwargs)
            return result
        return wrapper_function
    return decorator_function