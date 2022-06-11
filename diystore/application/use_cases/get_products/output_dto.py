from pydantic import BaseModel
from pydantic import constr
from pydantic import conint


class ProductOutputDTO(BaseModel):
    id: str
    ean: str
    name: str
    description: str
    price: str
    price_without_discount: str
    discount: str
    vat: str
    in_stock: constr(to_lower=True)
    height: str
    width: str
    length: str
    color: str
    material: str
    country_of_origin: str
    warranty: conint(strict=True)
    category_id: str
    category_name: str
    client_rating: str
    thumbnail_photo_url: str
    medium_size_photo_url: str
    large_size_photo_url: str
    vendor_id: str
    vendor_name: str
