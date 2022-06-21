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
    min_price = Decimal("0.01")
    max_price = Decimal("1_000_000")
    min_rating = Decimal("0")
    max_rating = Decimal("5")

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
    def _encode_uuid(_uuid: UUID) -> bytes:
        try:
            return _uuid.bytes
        except AttributeError:
            raise TypeError(f"object must be UUID not {type(_uuid).__name__}")

    def get_product(
        self, product_id: UUID, with_reviews: bool = False
    ) -> Optional[Product]:
        encoded_id = self._encode_uuid(product_id)
        with self._session as s:
            product: ProductOrmModel = s.get(ProductOrmModel, encoded_id)
            domain_entity = product.to_domain_entity(with_reviews) if product else None
        return domain_entity

    def _normalize_ranges(
        self, price_min, price_max, rating_min, rating_max
    ) -> tuple[Decimal]:
        if price_min < self.min_price or price_min > self.max_price:
            price_min = self.min_price
        if price_max < self.min_price or price_max > self.max_price:
            price_max = self.max_price
        if rating_min < self.min_rating or rating_min > self.max_rating:
            rating_min = self.min_rating
        if rating_max < self.min_rating or rating_max > self.max_rating:
            rating_max = self.max_rating
        return price_min, price_max, rating_min, rating_max

    def get_products(
        self,
        category_id: UUID,
        price_min: Decimal = min_price,
        price_max: Decimal = max_price,
        rating_min: Decimal = min_rating,
        rating_max: Decimal = max_rating,
        with_discounts_only: bool = False,
    ) -> list[Product]:
        encoded_id = self._encode_uuid(category_id)
        p_min, p_max, r_min, r_max = self._normalize_ranges(
            price_min, price_max, rating_min, rating_max
        )
        with self._session as s:
            query = (
                s.query(ProductOrmModel)
                .filter(
                    ProductOrmModel.category_id == encoded_id,
                    ProductOrmModel.base_price >= p_min,
                    ProductOrmModel.base_price <= p_max,
                    ProductOrmModel.rating >= r_min,
                    ProductOrmModel.rating <= r_max,
                )
            )
            if with_discounts_only:
                query = query.filter(ProductOrmModel.discount_id != None)
            products: list[ProductOrmModel] = query.all()
            domain_entities = [p.to_domain_entity() for p in products]
        return domain_entities

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
