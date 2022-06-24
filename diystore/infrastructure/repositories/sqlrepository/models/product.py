from uuid import UUID
from sqlalchemy import Column
from sqlalchemy import Numeric
from sqlalchemy import LargeBinary
from sqlalchemy import String
from sqlalchemy import Integer
from sqlalchemy import ForeignKey
from sqlalchemy import DateTime
from sqlalchemy.orm import validates
from sqlalchemy.orm import relationship

from . import Base
from . import tz
from .vat import VatOrmModel
from .discount import DiscountOrmModel
from .categories import TerminalCategoryOrmModel
from .vendor import ProductVendorOrmModel
from .review import ProductReviewOrmModel
from ..exceptions import OrmEntityNotFullyLoaded
from ..helpers import validate_id
from .....domain.entities.product import Product
from .....domain.entities.product import EAN13
from .....domain.entities.product import VAT
from .....domain.entities.product import ProductPrice
from .....domain.entities.product import ProductRating
from .....domain.entities.product import ProductDimensions
from .....domain.entities.product import ProductPhotoUrl
from .....domain.entities.product import ProductVendor
from .....domain.entities.product import ProductReview


class ProductOrmModel(Base):
    __tablename__ = "product"
    id = Column(LargeBinary(16), primary_key=True)
    ean = Column(String(13), nullable=False)
    name = Column(String(50), nullable=False)
    description = Column(String(3000))
    base_price = Column(Numeric(precision=8, scale=2), nullable=False)
    vat_id = Column(LargeBinary(16), ForeignKey("vat.id"), nullable=False)
    discount_id = Column(LargeBinary(16), ForeignKey("product_discount.id"))
    quantity = Column(Integer, nullable=False)
    creation_date = Column(DateTime(timezone=True), nullable=False)
    height = Column(Numeric(precision=6, scale=1))
    width = Column(Numeric(precision=6, scale=1))
    length = Column(Numeric(precision=6, scale=1))
    color = Column(String(30))
    material = Column(String(30))
    country_of_origin = Column(String(60), nullable=False)
    warranty = Column(Integer, nullable=False)
    category_id = Column(LargeBinary(16), ForeignKey("terminal_category.id"), nullable=False)
    rating = Column(Numeric(precision=2, scale=1))
    thumbnail_photo_url = Column(String(2000))
    medium_size_photo_url = Column(String(2000))
    large_size_photo_url = Column(String(2000))
    vendor_id = Column(LargeBinary(16), ForeignKey("vendor.id"), nullable=False)

    vat = relationship(VatOrmModel, lazy="joined")
    discount = relationship(DiscountOrmModel, lazy="joined")
    category = relationship(
        TerminalCategoryOrmModel, back_populates="products", lazy="joined"
    )
    vendor = relationship(
        ProductVendorOrmModel, back_populates="products", lazy="joined"
    )
    reviews = relationship(ProductReviewOrmModel, back_populates="product")

    @validates("id", "vat_id", "category_id", "vendor_id")
    def _validate_non_nullable_ids(self, key, _id):
        if _id is None:
            raise TypeError(f"{key} is a non-nullable field")
        if not isinstance(_id, (UUID, bytes, int, str)):
            raise TypeError("id must be an UUID, bytes, int or str object")
        return validate_id(_id, key)

    @validates("discount_id")
    def _validate_discount_id(self, key, _id):
        return validate_id(_id, key)

    def __repr__(self):
        return f"ProductOrmModel(ean={self.ean}, name={self.name}, price={self.base_price})"

    def to_domain_entity(self, with_reviews=False) -> Product:
        try:
            return Product.construct(
                id=UUID(bytes=self.id),
                ean=EAN13(self.ean),
                name=self.name,
                description=self.description,
                price=ProductPrice(
                    value=self.base_price,
                    vat=self.vat.to_domain_entity(),
                    discount=(
                        self.discount.to_domain_entity() if self.discount else None
                    ),
                ),
                quantity=self.quantity,
                creation_date=tz.convert(self.creation_date),
                dimensions=ProductDimensions(
                    height=self.height, width=self.width, length=self.length
                ),
                color=self.color.lower(),
                material=self.material,
                country_of_origin=self.country_of_origin,
                warranty=self.warranty,
                category=self.category.to_domain_entity(),
                rating=ProductRating(self.rating),
                reviews=(
                    [rev.to_domain_entity() for rev in self.reviews]
                    if with_reviews and self.reviews
                    else []
                ),
                photo_url=ProductPhotoUrl(
                    thumbnail=self.thumbnail_photo_url,
                    medium=self.medium_size_photo_url,
                    large=self.large_size_photo_url,
                ),
                vendor=self.vendor.to_domain_entity(),
            )
        except AttributeError:
            raise OrmEntityNotFullyLoaded

    @classmethod
    def from_domain_entity(cls, entity: Product) -> "ProductOrmModel":
        try:
            return cls(
                id=entity.get_id_in_bytes_format(),
                ean=entity.ean,
                name=entity.name,
                description=entity.description,
                base_price=entity.get_base_price(),
                vat_id=entity.get_vat_id_in_bytes_format(),
                discount_id=entity.get_discount_id_in_bytes_format(),
                quantity=entity.quantity,
                creation_date=entity.creation_date,
                height=entity.get_height(),
                width=entity.get_width(),
                length=entity.get_length(),
                color=entity.color,
                material=entity.material,
                country_of_origin=entity.country_of_origin,
                warranty=entity.warranty,
                category_id=entity.get_category_id_in_bytes_format(),
                rating=entity.rating,
                thumbnail_photo_url=entity.get_thumbnail_photo_url(),
                medium_size_photo_url=entity.get_medium_size_photo_url(),
                large_size_photo_url=entity.get_large_size_photo_url(),
                vendor_id=entity.get_vendor_id_in_bytes_format(),
                vat=VatOrmModel.from_domain_entity(entity.get_vat()),
                discount=DiscountOrmModel.from_domain_entity(entity.get_discount()),
                category=TerminalCategoryOrmModel.from_domain_entity(entity.category),
                vendor=ProductVendorOrmModel.from_domain_entity(entity.vendor),
                reviews=[
                    ProductReviewOrmModel.from_domain_entity(rev)
                    for rev in entity.reviews
                ],
            )
        except AttributeError:
            raise TypeError("entity must be of type Product")
