from typing import Type
from uuid import UUID
from decimal import Decimal

from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy import Numeric
from sqlalchemy import BINARY
from sqlalchemy.orm import validates

from . import Base
from ..helpers import validate_id
from .....domain.entities.product import VAT
from .....domain.helpers import round_decimal


class VatOrmModel(Base):
    __tablename__ = "vat"

    id = Column(BINARY(16), primary_key=True)
    name = Column(String(20), nullable=False)
    rate = Column(Numeric(precision=3, scale=2), nullable=False)

    @validates("id")
    def _validate_id(self, key, _id):
        if _id is None:
            raise TypeError
        return validate_id(_id, key)

    def to_domain_entity(self) -> VAT:
        return VAT(
            id=UUID(bytes=self.id),
            name=self.name,
            rate=round_decimal(Decimal(self.rate), "1.00"),
        )

    @classmethod
    def from_domain_entity(cls, entity: VAT) -> "VatOrmModel":
        if not isinstance(entity, VAT):
            raise TypeError(f"entity must be of type VAT")
        return cls(id=entity.id.bytes, name=entity.name, rate=entity.rate)

    def __repr__(self):
        return f"VatOrmModel(id={UUID(bytes=self.id)}, name={self.name!r}, rate={self.rate!r})"
