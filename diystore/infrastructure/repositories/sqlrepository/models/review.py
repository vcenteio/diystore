from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy import Numeric
from sqlalchemy import BINARY
from sqlalchemy import ForeignKey
from sqlalchemy import DateTime
from sqlalchemy.orm import validates

from . import Base
from . import tz
from ..helpers import validate_id
from .....domain.entities.product import ProductReview


class ProductReviewOrmModel(Base):
    __tablename__ = "product_review"
    id = Column(BINARY(16), primary_key=True)
    product_id = Column(BINARY(16), nullable=False)
    client_id = Column(BINARY(16), nullable=False)
    rating = Column(Numeric(precision=2, scale=1), nullable=False)
    creation_date = Column(DateTime(timezone=True), nullable=False)
    feedback = Column(String(3000))

    @validates("id", "product_id", "client_id")
    def _validate_id(self, key, _id):
        return validate_id(_id, key)

    def to_domain_entity(self) -> ProductReview:
        return ProductReview(
            id=self.id,
            product_id=self.product_id,
            client_id=self.client_id,
            rating=self.rating,
            creation_date=tz.convert(self.creation_date),
            feedback=self.feedback,
        )

    @classmethod
    def from_domain_entity(cls, entity: ProductReview) -> "ProductReviewOrmModel":
        try:
            return cls(
                id=entity.id.bytes,
                product_id=entity.product_id.bytes,
                client_id=entity.client_id.bytes,
                rating=entity.rating,
                creation_date=entity.creation_date,
                feedback=entity.feedback,
            )
        except AttributeError:
            raise TypeError("entity must be of type ProductReview")
