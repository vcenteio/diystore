from decimal import Decimal


def round_decimal(decimal: Decimal, template: str):
    return decimal.quantize(Decimal(template))
