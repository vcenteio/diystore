from uuid import UUID

from pydantic import BaseModel
from pydantic import constr
from pydantic import conint
from pydantic import validator

from .....domain.entities.product import Product


class GetProductOutputDTO(BaseModel):
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

    class Config:
        frozen = True

    @validator("id", pre=True)
    def _validate_id(cls, _id):
        if isinstance(_id, UUID):
            return _id.hex
        return _id

    @classmethod
    def from_product(cls, product: Product):
        dimensions = product.get_dimensions_dict()
        return cls(
            id=product.id.hex,
            ean=product.ean,
            name=product.name,
            description=product.description,
            price=product.get_final_price(),
            price_without_discount=product.get_final_price(with_discount=False),
            discount=product.get_discount_rate(),
            vat=product.get_vat_rate(),
            in_stock=product.quantity is not 0,
            height=dimensions["height"],
            width=dimensions["width"],
            length=dimensions["length"],
            color=product.color,
            material=product.material,
            country_of_origin=product.country_of_origin,
            warranty=product.warranty,
            category_id=product.get_category_id().hex,
            category_name=product.get_category_name(),
            client_rating=product.get_client_rating(),
            thumbnail_photo_url=product.get_thumbnail_photo_url(),
            medium_size_photo_url=product.get_medium_size_photo_url(),
            large_size_photo_url=product.get_large_size_photo_url(),
            vendor_id=product.get_vendor_id().hex,
            vendor_name=product.get_vendor_name(),
        )
