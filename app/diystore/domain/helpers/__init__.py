from decimal import Decimal
from functools import wraps


def round_decimal(decimal: Decimal, template: str):
    return decimal.quantize(Decimal(template))


def optional(e: Exception = AttributeError):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except e:
                return None

        return wrapper

    return decorator
