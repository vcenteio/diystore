from functools import wraps

from flask import g


def request_controller(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        return f(*args, **kwargs, controller=g.controller)

    return wrapper
