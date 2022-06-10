from abc import ABC
from abc import abstractmethod
from decimal import Decimal
from uuid import UUID


class Repository(ABC):
    @abstractmethod
    def get_products_ordering_by_rating(
        self,
        category_id: UUID,
        price_range: tuple[Decimal, Decimal],
        rating_range: tuple[Decimal, Decimal],
        with_discounts_only: bool = False,
        descending: bool = True
    ):
        ...

    @abstractmethod
    def get_products_ordering_by_price(
        self,
        category_id: UUID,
        price_range: tuple[Decimal, Decimal],
        rating_range: tuple[Decimal, Decimal],
        with_discounts_only: bool = False,
        descending: bool = True
    ):
        ...
