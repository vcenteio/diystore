from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy import Numeric
from sqlalchemy import LargeBinary
from sqlalchemy import DateTime
from sqlalchemy.orm import validates

from . import Base
from . import tz
from ..helpers import validate_id
from .....domain.entities.product.discount import Discount


class DiscountOrmModel(Base):
    __tablename__ = "product_discount"

    id = Column(LargeBinary(16), primary_key=True)
    name = Column(String(50))
    rate = Column(Numeric(precision=3, scale=2))
    creation_date = Column(DateTime(timezone=True))
    expiry_date = Column(DateTime(timezone=True))

    @validates("id")
    def _validate_id(self, key, _id):
        return validate_id(_id, key)

    def to_domain_entity(self) -> Discount:
        return Discount(
            id=self.id,
            name=self.name,
            rate=self.rate,
            creation_date=tz.convert(self.creation_date),
            expiry_date=tz.convert(self.expiry_date),
        )

    @classmethod
    def from_domain_entity(cls, entity: Discount) -> "DiscountOrmModel":
        try:
            return cls(
                id=entity.id.bytes,
                name=entity.name,
                rate=entity.rate,
                creation_date=entity.creation_date,
                expiry_date=entity.expiry_date,
            )
        except AttributeError:
            raise TypeError(
                f"entity must be of type Discount, not {type(entity).__name__}"
            )
        
    def __repr__(self):
        return (
            f"DiscountOrmModel(id={self.id!r}, name={self.name!r}, rate={self.rate!r}, "
            f"creation_date={self.creation_date!r}, expiry_date={self.expiry_date!r})"
        )
