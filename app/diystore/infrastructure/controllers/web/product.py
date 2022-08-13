from typing import Optional
from typing import Callable
from functools import wraps
from functools import partial

from pydantic import ValidationError

from .exceptions import InvalidQueryArgument
from .exceptions import InvalidProductID
from .exceptions import ProductNotFound
from ...cache.interfaces import ProductCache
from ....application.dto import DTO
from ....application.usecases.product import ProductRepository
from ....application.usecases.product import get_product_use_case
from ....application.usecases.product import get_products_use_case
from ....application.usecases.product import GetProductInputDTO
from ....application.usecases.product import GetProductsInputDTO
from ....application.usecases.product import ProductOrderingCriteria
from ....application.usecases.product import OrderingProperty
from ....application.usecases.product import OrderingType
from ....application.dto import DTO


class ProductController:
    def __init__(
        self, repo: ProductRepository, cache: ProductCache, presenter: Callable
    ):
        self._repo = repo
        self._cache_repo = cache
        self._presenter = presenter

    def _select_cache_methods(self, args, kwargs):
        c = self._cache_repo
        if len(kwargs):
            return partial(c.get_many, **kwargs), partial(c.set_many, **kwargs)
        return partial(c.get_one, _id=args[0]), partial(c.set_one, _id=args[0])

    @staticmethod
    def _cache(f):
        @wraps(f)
        def wrapper(self: "ProductController", *args, **kwargs):
            get_method, set_method = self._select_cache_methods(args, kwargs)
            cached_repr = get_method()
            if cached_repr is None:
                new_repr = f(self, **kwargs) if len(kwargs) else f(self, args[0])
                set_method(representation=new_repr)
                return new_repr
            return cached_repr

        return wrapper

    def _generate_presentation(self, output_dto: DTO) -> str:
        return self._presenter(output_dto)

    @_cache
    def get_one(self, product_id: str) -> Optional[str]:
        try:
            input_dto = GetProductInputDTO(product_id=product_id)
        except ValidationError:
            raise InvalidProductID(_id=product_id)
        output_dto = get_product_use_case(input_dto, self._repo)
        if output_dto is None:
            raise ProductNotFound(_id=product_id)
        return self._generate_presentation(output_dto)

    def _get_ordering_property(self, order_by: str):
        if order_by == "rating":
            return OrderingProperty.RATING
        if order_by == "price":
            return OrderingProperty.PRICE
        raise InvalidQueryArgument(None, "order_by")

    def _get_ordering_type(self, order_type: str):
        if order_type in ("asc", "ascending"):
            return OrderingType.ASCENDING
        if order_type in ("desc", "descending"):
            return OrderingType.DESCESDING
        raise InvalidQueryArgument(None, "order_type")

    def _get_ordering_criteria(self, order_by, order_type):
        ordering_property = self._get_ordering_property(order_by)
        ordering_type = self._get_ordering_type(order_type)
        return ProductOrderingCriteria(property=ordering_property, type=ordering_type)

    def _create_input_dto_for_get_many(
        self,
        cid: str,
        pmin: float,
        pmax: float,
        rmin: float,
        rmax: float,
        order_by: str,
        order_type: str,
        with_discounts_only: bool,
    ):
        ordering_criteria = self._get_ordering_criteria(order_by, order_type)
        try:
            return GetProductsInputDTO(
                category_id=cid,
                price_min=pmin,
                price_max=pmax,
                rating_min=rmin,
                rating_max=rmax,
                ordering_criteria=ordering_criteria,
                with_discounts_only=with_discounts_only,
            )
        except ValidationError as e:
            loc = e.errors()[0].get("loc")[0]
            raise InvalidQueryArgument(None, loc)

    @_cache
    def get_many(
        self,
        *,
        category_id: str,
        price_min: float = 0.01,
        price_max: float = 1_000_000,
        rating_min: float = 0,
        rating_max: float = 5,
        order_by: str = "rating",
        order_type: str = "descending",
        with_discounts_only: bool = False,
    ):
        input_dto = self._create_input_dto_for_get_many(
            category_id,
            price_min,
            price_max,
            rating_min,
            rating_max,
            order_by,
            order_type,
            with_discounts_only,
        )
        output_dto = get_products_use_case(input_dto, self._repo)
        return self._generate_presentation(output_dto)
