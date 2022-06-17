from sqlalchemy import Column
from sqlalchemy import Numeric
from sqlalchemy import BINARY
from sqlalchemy import String
from sqlalchemy import Integer
from sqlalchemy import ForeignKey
from sqlalchemy import DateTime
from sqlalchemy.orm import validates
from sqlalchemy.orm import relationship

from . import Base
from ..helpers import validate_id
from .....domain.entities.product import Product


class ProductOrmModel(Base):
    __tablename__ = "product"
    id = Column(BINARY(16), primary_key=True)
    ean = Column(String(13), nullable=False)
    name = Column(String(50), nullable=False)
    description = Column(String(3000))
    base_price = Column(Numeric(precision=8, scale=2), nullable=False)
    vat_id = Column(BINARY(16), ForeignKey("vat.id"), nullable=False)
    discount_id = Column(BINARY(16), ForeignKey("product_discount.id"))
    quantity = Column(Integer, nullable=False)
    creation_date = Column(DateTime(timezone=True), nullable=False)
    height = Column(Numeric(precision=6, scale=1))
    width = Column(Numeric(precision=6, scale=1))
    length = Column(Numeric(precision=6, scale=1))
    color = Column(String(30))
    material = Column(String(30))
    country_of_origin = Column(String(60), nullable=False)
    warranty = Column(Integer, nullable=False)
    category_id = Column(BINARY(16), ForeignKey("terminal_category.id"), nullable=False)
    rating = Column(Numeric(precision=2, scale=1))
    thumbnail_photo_url = Column(String(2000))
    medium_size_photo_url = Column(String(2000))
    large_size_photo_url = Column(String(2000))
    vendor_id = Column(BINARY(16), ForeignKey("vendor.id"), nullable=False)

    vat = relationship("VatOrmModel")
    discount = relationship("DiscountOrmModel")
    category = relationship("TerminalCategoryOrmModel")
    vendor = relationship("ProductVendorOrmModel")

    @validates("id", "vat_id", "discount_id", "category_id", "vendor_id")
    def _validate_id(self, key, _id):
        return validate_id(_id, key)

    def __repr__(self):
        return f"ProductOrmModel(ean={self.ean}, name={self.name}, price={self.base_price})"
