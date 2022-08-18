from uuid import UUID
from decimal import Decimal
from typing import Optional

from sqlalchemy import Column
from sqlalchemy.orm import joinedload
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import create_engine
from sqlalchemy.exc import ArgumentError
from pydantic import AnyUrl

from .models import Base
from .models.product import ProductOrmModel
from .models.categories import TopLevelCategoryOrmModel
from .models.categories import MidLevelCategoryOrmModel
from ....domain.entities.product import Product
from ....domain.entities.product import TopLevelProductCategory
from ....domain.entities.product import MidLevelProductCategory
from ....application.usecases.product import ProductRepository


class SQLProductRepository(ProductRepository):
    min_price = Decimal("0.01")
    max_price = Decimal("1_000_000")
    min_rating = Decimal("0")
    max_rating = Decimal("5")

    def __init__(
        self,
        scheme: str,
        host: str,
        port: int = None,
        user: str = None,
        password: str = None,
        dbname: str = None,
        base=Base,
    ):
        db_url = AnyUrl.build(
            scheme=scheme,
            host=host,
            port=str(port) if port is not None else None,
            user=user,
            password=password,
            path=f"/{dbname}" if dbname is not None else None,
        )
        try:
            self._engine = create_engine(db_url, future=True)
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

    def _generate_get_products_query(
        self,
        category_id: UUID,
        session: Session,
        price_min: Decimal = min_price,
        price_max: Decimal = max_price,
        rating_min: Decimal = min_rating,
        rating_max: Decimal = max_rating,
        with_discounts_only: bool = False,
        orderby_attr: Column = None,
        descending: bool = False,
    ):
        encoded_id = self._encode_uuid(category_id)
        p_min, p_max, r_min, r_max = self._normalize_ranges(
            price_min, price_max, rating_min, rating_max
        )
        query = session.query(ProductOrmModel).filter(
            ProductOrmModel.category_id == encoded_id,
            ProductOrmModel.base_price >= p_min,
            ProductOrmModel.base_price <= p_max,
            ProductOrmModel.rating >= r_min,
            ProductOrmModel.rating <= r_max,
        )
        if with_discounts_only:
            query = query.filter(ProductOrmModel.discount_id != None)
        if orderby_attr is not None:
            query = query.order_by(orderby_attr.desc() if descending else orderby_attr)
        return query

    def _get_products(
        self,
        category_id: UUID,
        price_min: Decimal = min_price,
        price_max: Decimal = max_price,
        rating_min: Decimal = min_rating,
        rating_max: Decimal = max_rating,
        with_discounts_only: bool = False,
        orderby_attr: Column = None,
        descending: bool = False,
    ) -> list[Product]:
        with self._session as s:
            query = self._generate_get_products_query(
                category_id,
                s,
                price_min,
                price_max,
                rating_min,
                rating_max,
                with_discounts_only,
                orderby_attr,
                descending,
            )
            products: list[ProductOrmModel] = query.all()
            domain_entities = [p.to_domain_entity() for p in products]
        return domain_entities

    def get_products(
        self,
        category_id: UUID,
        price_min: Decimal = Decimal("0.01"),
        price_max: Decimal = Decimal("1_000_000"),
        rating_min: Decimal = Decimal("0"),
        rating_max: Decimal = Decimal("5"),
        with_discounts_only: bool = False,
    ) -> list[Product]:
        return self._get_products(
            category_id,
            price_min,
            price_max,
            rating_min,
            rating_max,
            with_discounts_only,
        )

    def get_products_ordering_by_rating(
        self,
        category_id: UUID,
        price_min: Decimal = Decimal("0.01"),
        price_max: Decimal = Decimal("1_000_000"),
        rating_min: Decimal = Decimal("0"),
        rating_max: Decimal = Decimal("5"),
        with_discounts_only: bool = False,
        descending: bool = True,
    ) -> list[Product]:
        orderby_attr = ProductOrmModel.rating
        return self._get_products(
            category_id,
            price_min,
            price_max,
            rating_min,
            rating_max,
            with_discounts_only,
            orderby_attr=orderby_attr,
            descending=descending,
        )

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
        orderby_attr = ProductOrmModel.base_price
        return self._get_products(
            category_id,
            price_min,
            price_max,
            rating_min,
            rating_max,
            with_discounts_only,
            orderby_attr=orderby_attr,
            descending=descending,
        )

    def get_top_level_category(
        self, category_id: UUID
    ) -> Optional[TopLevelProductCategory]:
        encoded_id = self._encode_uuid(category_id)
        with self._session as s:
            orm_category: TopLevelCategoryOrmModel = s.get(
                TopLevelCategoryOrmModel, encoded_id
            )
            domain_entity = orm_category.to_domain_entity() if orm_category else None
        return domain_entity

    def get_top_level_categories(self) -> tuple[TopLevelProductCategory]:
        with self._session as s:
            categories = s.query(TopLevelCategoryOrmModel).all()
        return tuple(c.to_domain_entity() for c in categories)

    def get_mid_level_category(
        self, category_id: UUID
    ) -> Optional[MidLevelProductCategory]:
        encoded_id = self._encode_uuid(category_id)
        with self._session as s:
            orm_category: MidLevelCategoryOrmModel = s.get(
                MidLevelCategoryOrmModel, encoded_id
            )
            domain_entity = orm_category.to_domain_entity() if orm_category else None
        return domain_entity

    def get_mid_level_categories(
        self, parent_id: UUID
    ) -> Optional[tuple[MidLevelProductCategory]]:
        encoded_id = self._encode_uuid(parent_id)
        with self._session as s:
            top_category: TopLevelCategoryOrmModel = s.get(
                TopLevelCategoryOrmModel,
                encoded_id,
                options=(joinedload(TopLevelCategoryOrmModel.children),),
            )
            if top_category is None:
                return None
            categories = tuple(c.to_domain_entity() for c in top_category.children)
        return categories
