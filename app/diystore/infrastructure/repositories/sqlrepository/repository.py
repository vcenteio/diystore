from uuid import UUID
from decimal import Decimal
from typing import Optional
from functools import wraps

from sqlalchemy import Column
from sqlalchemy.orm import joinedload
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import create_engine
from sqlalchemy.exc import ArgumentError
from pydantic import AnyUrl

from .models import Base
from .models.product import ProductOrmModel
from .models.product import ProductVendorOrmModel
from .models.categories import TopLevelCategoryOrmModel
from .models.categories import MidLevelCategoryOrmModel
from .models.categories import TerminalCategoryOrmModel
from .models.review import ProductReviewOrmModel
from ....domain.entities.product import Product
from ....domain.entities.product import ProductVendor
from ....domain.entities.product import ProductReview
from ....domain.entities.product import TopLevelProductCategory
from ....domain.entities.product import MidLevelProductCategory
from ....domain.entities.product import TerminalLevelProductCategory
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
        echo: bool = False,
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
            self._engine = create_engine(db_url, future=True, echo=echo)
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

    @staticmethod
    def _crud_operation(f):
        @wraps(f)
        def wrapper(self: "SQLProductRepository", *args, **kwargs):
            with self._session as s:
                return f(self, *args, **kwargs, _session=s)

        return wrapper

    @_crud_operation
    def get_product(
        self, product_id: UUID, with_reviews: bool = False, _session: Session = None
    ) -> Optional[Product]:
        encoded_id = self._encode_uuid(product_id)
        product: ProductOrmModel = _session.get(ProductOrmModel, encoded_id)
        return product.to_domain_entity(with_reviews) if product else None

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
        _session: Session,
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
        query = _session.query(ProductOrmModel).filter(
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
        _session: Session = None,
    ) -> tuple[Product]:
        query = self._generate_get_products_query(
            category_id,
            _session,
            price_min,
            price_max,
            rating_min,
            rating_max,
            with_discounts_only,
            orderby_attr,
            descending,
        )
        products: list[ProductOrmModel] = query.all()
        return tuple(p.to_domain_entity() for p in products)

    @_crud_operation
    def get_products(
        self,
        category_id: UUID,
        price_min: Decimal = Decimal("0.01"),
        price_max: Decimal = Decimal("1_000_000"),
        rating_min: Decimal = Decimal("0"),
        rating_max: Decimal = Decimal("5"),
        with_discounts_only: bool = False,
        _session: Session = None,
    ) -> tuple[Product]:
        return self._get_products(
            category_id,
            price_min,
            price_max,
            rating_min,
            rating_max,
            with_discounts_only,
            _session=_session,
        )

    @_crud_operation
    def get_products_ordering_by_rating(
        self,
        category_id: UUID,
        price_min: Decimal = Decimal("0.01"),
        price_max: Decimal = Decimal("1_000_000"),
        rating_min: Decimal = Decimal("0"),
        rating_max: Decimal = Decimal("5"),
        with_discounts_only: bool = False,
        descending: bool = True,
        _session: Session = None,
    ) -> tuple[Product]:
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
            _session=_session,
        )

    @_crud_operation
    def get_products_ordering_by_price(
        self,
        category_id: UUID,
        price_min: Decimal = Decimal("0.01"),
        price_max: Decimal = Decimal("1_000_000"),
        rating_min: Decimal = Decimal("0"),
        rating_max: Decimal = Decimal("5"),
        with_discounts_only: bool = False,
        descending: bool = False,
        _session: Session = None,
    ) -> tuple[Product]:
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
            _session=_session,
        )

    @_crud_operation
    def get_top_level_category(
        self, category_id: UUID, _session: Session = None
    ) -> Optional[TopLevelProductCategory]:
        encoded_id = self._encode_uuid(category_id)
        orm_category: TopLevelCategoryOrmModel = _session.get(
            TopLevelCategoryOrmModel, encoded_id
        )
        return orm_category.to_domain_entity() if orm_category else None

    @_crud_operation
    def get_top_level_categories(
        self, _session: Session = None
    ) -> tuple[TopLevelProductCategory]:
        categories = _session.query(TopLevelCategoryOrmModel).all()
        return tuple(c.to_domain_entity() for c in categories)

    @_crud_operation
    def get_mid_level_category(
        self, category_id: UUID, _session: Session = None
    ) -> Optional[MidLevelProductCategory]:
        encoded_id = self._encode_uuid(category_id)
        orm_category: MidLevelCategoryOrmModel = _session.get(
            MidLevelCategoryOrmModel, encoded_id
        )
        return orm_category.to_domain_entity() if orm_category else None

    @_crud_operation
    def get_mid_level_categories(
        self, parent_id: UUID, _session: Session = None
    ) -> Optional[tuple[MidLevelProductCategory]]:
        encoded_id = self._encode_uuid(parent_id)
        top_category: TopLevelCategoryOrmModel = _session.get(
            TopLevelCategoryOrmModel,
            encoded_id,
            options=(joinedload(TopLevelCategoryOrmModel.children),),
        )
        if top_category is None:
            return None
        return tuple(c.to_domain_entity() for c in top_category.children)

    @_crud_operation
    def get_terminal_level_category(
        self, category_id: UUID, _session: Session
    ) -> Optional[TerminalLevelProductCategory]:
        encoded_id = self._encode_uuid(category_id)
        orm_category: TerminalCategoryOrmModel = _session.get(
            TerminalCategoryOrmModel, encoded_id
        )
        return orm_category.to_domain_entity() if orm_category else None

    @_crud_operation
    def get_terminal_level_categories(
        self, parent_id: UUID, _session: Session
    ) -> Optional[tuple[TerminalLevelProductCategory]]:
        encoded_id = self._encode_uuid(parent_id)
        parent: MidLevelCategoryOrmModel = _session.get(
            MidLevelCategoryOrmModel,
            encoded_id,
            options=(joinedload(MidLevelCategoryOrmModel.children),),
        )
        if parent is not None:
            return tuple(c.to_domain_entity() for c in parent.children)
        return None

    @_crud_operation
    def get_vendor(self, vendor_id: UUID, _session: Session) -> Optional[ProductVendor]:
        encoded_id = self._encode_uuid(vendor_id)
        vendor: ProductVendorOrmModel = _session.get(ProductVendorOrmModel, encoded_id)
        return vendor.to_domain_entity() if vendor is not None else None

    @_crud_operation
    def get_vendors(self, _session: Session) -> tuple[ProductVendor]:
        orm_vendors = _session.query(ProductVendorOrmModel)
        return tuple(v.to_domain_entity() for v in orm_vendors)

    @_crud_operation
    def get_review(self, review_id: UUID, _session: Session) -> Optional[ProductReview]:
        encoded_id = self._encode_uuid(review_id)
        orm_review: ProductReviewOrmModel = _session.get(
            ProductReviewOrmModel, encoded_id
        )
        if orm_review is not None:
            return orm_review.to_domain_entity()
        return None

    @_crud_operation
    def get_reviews(
        self, product_id: UUID, _session: Session
    ) -> Optional[tuple[ProductReview]]:
        encoded_id = self._encode_uuid(product_id)
        product = (
            _session.get(
                ProductOrmModel,
                encoded_id,
                options=(joinedload(ProductOrmModel.reviews),),
            )
        )
        if product is not None:
            return tuple(r.to_domain_entity() for r in product.reviews)
        return None
