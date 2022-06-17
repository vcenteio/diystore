from sqlalchemy import Column
from sqlalchemy import BINARY
from sqlalchemy import String
from sqlalchemy.orm import validates

from . import Base
from ..helpers import validate_id
from .....domain.entities.product import ProductVendor


class ProductVendorOrmModel(Base):
    __tablename__ = "vendor"
    id = Column(BINARY(16), primary_key=True)
    name = Column(String(50))
    description = Column(String(3000))
    logo_url = Column(String(2000))

    @validates("id")
    def _validate_id(self, key, _id):
        return validate_id(_id, key)

    def to_domain_entity(self) -> ProductVendor:
        return ProductVendor(
            id=self.id,
            name=self.name,
            description=self.description,
            logo_url=self.logo_url,
        )

    @classmethod
    def from_domain_entity(cls, entity: ProductVendor) -> "ProductVendorOrmModel":
        try:
            return cls(
                id=entity.id.bytes,
                name=entity.name,
                description=entity.description,
                logo_url=entity.logo_url,
            )
        except AttributeError:
            raise TypeError("entity must be of type ProductVendor")
