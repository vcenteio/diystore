from uuid import UUID
from decimal import Decimal
from typing import Optional

from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import create_engine
from sqlalchemy.exc import ArgumentError

from .models import Base
from .models.product import ProductOrmModel
from ....domain.entities.product import Product
from ....application.usecases.product import ProductRepository


class SQLProductRepository(ProductRepository):
    @staticmethod
    def _validate_url(url):
        if not isinstance(url, str):
            raise TypeError(f"wrong type for url: {type(url).__name__}")
        return url

    def __init__(self, db_url: str, base=Base):
        self._db_url = self._validate_url(db_url)
        try:
            self._engine = create_engine(self._db_url)
        except ArgumentError:
            raise ValueError(f"invalid url passed as argument: {db_url}")
        base.metadata.create_all(self._engine)
        self._session_factory = sessionmaker(self._engine)

    @property
    def _session(self) -> Session:
        return self._session_factory()

    @staticmethod
    def _encode_product_id(product_id: UUID) -> bytes:
        try:
            return product_id.bytes
        except AttributeError:
            raise TypeError(f"product_id must be UUID not {type(product_id).__name__}")

    def get_product(
        self, product_id: UUID, with_reviews: bool = False
    ) -> Optional[Product]:
        encoded_id = self._encode_product_id(product_id)
        with self._session as s:
            product: ProductOrmModel = s.get(ProductOrmModel, encoded_id)
            domain_entity = product.to_domain_entity(with_reviews) if product else None
        return domain_entity

    def get_products(
        self,
        category_id: UUID,
        price_min: Decimal = Decimal("0.01"),
        price_max: Decimal = Decimal("1_000_000"),
        rating_min: Decimal = Decimal("0"),
        rating_max: Decimal = Decimal("5"),
        with_discounts_only: bool = False,
    ):
        pass

    def get_products_ordering_by_rating(
        self,
        category_id: UUID,
        price_min: Decimal = Decimal("0.01"),
        price_max: Decimal = Decimal("1_000_000"),
        rating_min: Decimal = Decimal("0"),
        rating_max: Decimal = Decimal("5"),
        with_discounts_only: bool = False,
        descending: bool = False,
    ) -> list[Product]:
        pass

    def get_products_ordering_by_price(
        self,
        category_id: UUID,
        price_min: Decimal = Decimal("0.01"),
        price_max: Decimal = Decimal("1_000_000"),
        rating_min: Decimal = Decimal("0"),
        rating_max: Decimal = Decimal("5"),
        with_discounts_only: bool = False,
        descending: bool = False,
    ) -> list[Product]:
        pass
