from abc import ABC
from abc import abstractmethod
from decimal import Decimal
from typing import Optional
from uuid import UUID

from ....domain.entities.product import Product
from ....domain.entities.product import TopLevelProductCategory
from ....domain.entities.product import MidLevelProductCategory
from ....domain.entities.product import TerminalLevelProductCategory


class ProductRepository(ABC):
    @abstractmethod
    def get_product(
        self, product_id: UUID, with_reviews: bool = False
    ) -> Optional[Product]:
        ...

    @abstractmethod
    def get_products(
        self,
        category_id: UUID,
        price_min: Decimal = Decimal("0.01"),
        price_max: Decimal = Decimal("1_000_000"),
        rating_min: Decimal = Decimal("0"),
        rating_max: Decimal = Decimal("5"),
        with_discounts_only: bool = False,
    ) -> Product:
        ...

    @abstractmethod
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
        ...

    @abstractmethod
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
        ...

    @abstractmethod
    def get_top_level_category(
        self, category_id: UUID
    ) -> Optional[TopLevelProductCategory]:
        ...

    @abstractmethod
    def get_top_level_categories(self) -> tuple[TopLevelProductCategory]:
        ...

    @abstractmethod
    def get_mid_level_category(
        self, category_id: UUID
    ) -> Optional[MidLevelProductCategory]:
        ...

    @abstractmethod
    def get_mid_level_categories(
        self, parent_id: UUID
    ) -> Optional[tuple[MidLevelProductCategory]]:
        ...

    @abstractmethod
    def get_terminal_level_category(
        self, category_id: UUID
    ) -> Optional[TerminalLevelProductCategory]:
        ...
