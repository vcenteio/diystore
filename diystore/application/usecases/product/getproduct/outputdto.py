from uuid import UUID
from typing import Optional

from pydantic import BaseModel
from pydantic import constr
from pydantic import validator

from ....dto import DTO
from .....domain.entities.product import Product


class GetProductOutputDTO(BaseModel, DTO):
    id: str
    ean: str
    name: str
    description: Optional[str]
    price: str
    price_without_discount: str
    discount: Optional[str]
    vat: str
    in_stock: constr(to_lower=True)
    rating: Optional[str]
    height: Optional[str]
    width: Optional[str]
    length: Optional[str]
    color: Optional[str]
    material: Optional[str]
    country_of_origin: str
    warranty: int
    category_id: str
    category_name: str
    client_rating: str
    thumbnail_photo_url: Optional[str]
    medium_size_photo_url: Optional[str]
    large_size_photo_url: Optional[str]
    vendor_id: str
    vendor_name: str

    class Config:
        frozen = True

    @validator("id", pre=True)
    def _validate_id(cls, _id):
        if isinstance(_id, UUID):
            return _id.hex
        return _id

    @classmethod
    def from_product(cls, product: Product):
        return cls(
            id=product.get_id_in_hex_format(),
            ean=product.ean,
            name=product.name,
            description=product.description,
            price=product.get_final_price(),
            price_without_discount=product.get_final_price_without_discount(),
            discount=product.get_discount_rate(),
            vat=product.get_vat_rate(),
            in_stock=product.quantity > 0,
            rating=product.get_client_rating(),
            height=product.get_height(),
            width=product.get_width(),
            length=product.get_length(),
            color=product.color,
            material=product.material,
            country_of_origin=product.country_of_origin,
            warranty=product.warranty,
            category_id=product.get_category_id_in_hex_format(),
            category_name=product.get_category_name(),
            client_rating=product.get_client_rating(),
            thumbnail_photo_url=product.get_thumbnail_photo_url(),
            medium_size_photo_url=product.get_medium_size_photo_url(),
            large_size_photo_url=product.get_large_size_photo_url(),
            vendor_id=product.get_vendor_id_in_hex_format(),
            vendor_name=product.get_vendor_name(),
        )
