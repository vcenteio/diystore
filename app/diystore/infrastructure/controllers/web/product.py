from typing import Callable
from functools import wraps

from pydantic import ValidationError

from .exceptions import InvalidQueryArgument
from .exceptions import InvalidVendorID
from .exceptions import InvalidProductID
from .exceptions import InvalidCategoryID
from .exceptions import InvalidReviewID
from .exceptions import ProductNotFound
from .exceptions import VendorNotFound
from .exceptions import ReviewNotFound
from .exceptions import TopCategoryNotFound
from .exceptions import MidCategoryNotFound
from .exceptions import TerminalCategoryNotFound
from ...cache.interfaces import Cache
from ....application.dto import DTO
from ....application.usecases.product import ProductRepository
from ....application.usecases.product import get_product_use_case
from ....application.usecases.product import get_products_use_case
from ....application.usecases.product import GetProductInputDTO
from ....application.usecases.product import GetProductsInputDTO
from ....application.usecases.product import ProductOrderingCriteria
from ....application.usecases.product import OrderingProperty
from ....application.usecases.product import OrderingType
from ....application.usecases.product import get_top_level_category
from ....application.usecases.product import GetTopLevelCategoryInputDTO
from ....application.usecases.product import get_top_level_categories
from ....application.usecases.product import GetMidLevelCategoryInputDTO
from ....application.usecases.product import get_mid_level_category
from ....application.usecases.product import get_mid_level_categories
from ....application.usecases.product import GetMidLevelCategoriesInputDTO
from ....application.usecases.product import GetTerminalLevelCategoryInputDTO
from ....application.usecases.product import get_terminal_level_category
from ....application.usecases.product import GetTerminalLevelCategoriesInputDTO
from ....application.usecases.product import get_terminal_level_categories
from ....application.usecases.product import GetProductVendorInputDTO
from ....application.usecases.product import get_vendor
from ....application.usecases.product import get_vendors
from ....application.usecases.product import GetProductReviewInputDTO
from ....application.usecases.product import get_review
from ....application.usecases.product import GetProductReviewsInputDTO
from ....application.usecases.product import get_reviews


class ProductController:
    def __init__(self, repo: ProductRepository, cache: Cache, presenter: Callable):
        self._repo = repo
        self._cache_repo = cache
        self._presenter = presenter

    @staticmethod
    def _cache(f):
        @wraps(f)
        def wrapper(self: "ProductController", **kwargs):
            args = dict(cname=type(self).__name__, fname=f.__name__, **kwargs)
            cached_repr = self._cache_repo.get(**args)
            if cached_repr is None:
                new_repr = f(self, **kwargs)
                self._cache_repo.set(new_repr, **args)
                return new_repr
            return cached_repr

        return wrapper

    def _generate_representation(self, output_dto: DTO) -> str:
        return self._presenter(output_dto)

    @_cache
    def get_one(self, *, product_id: str) -> str:
        try:
            input_dto = GetProductInputDTO(product_id=product_id)
        except ValidationError:
            raise InvalidProductID(_id=product_id)
        output_dto = get_product_use_case(input_dto, self._repo)
        if output_dto is None:
            raise ProductNotFound(_id=product_id)
        return self._generate_representation(output_dto)

    _ordering_property_map = {
        "rating": OrderingProperty.RATING,
        "price": OrderingProperty.PRICE,
    }

    _ordering_type_map = {
        "asc": OrderingType.ASCENDING,
        "ascending": OrderingType.ASCENDING,
        "desc": OrderingType.DESCESDING,
        "descending": OrderingType.DESCESDING,
    }

    def _get_ordering_property(self, order_by: str):
        try:
            return self._ordering_property_map[order_by]
        except KeyError:
            raise InvalidQueryArgument(parameter="order_by")

    def _get_ordering_type(self, order_type: str):
        try:
            return self._ordering_type_map[order_type]
        except KeyError:
            raise InvalidQueryArgument(parameter="order_type")

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
            parameter = e.errors()[0].get("loc")[0]
            raise InvalidQueryArgument(parameter=parameter)

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
        return self._generate_representation(output_dto)

    @_cache
    def get_top_category(self, *, category_id: str) -> str:
        try:
            input_dto = GetTopLevelCategoryInputDTO(category_id=category_id)
        except ValidationError:
            raise InvalidCategoryID(_id=category_id)
        output_dto = get_top_level_category(input_dto, self._repo)
        if output_dto is None:
            raise TopCategoryNotFound(_id=category_id)
        return self._generate_representation(output_dto)

    @_cache
    def get_top_categories(self) -> str:
        output_dto = get_top_level_categories(self._repo)
        return self._generate_representation(output_dto)

    @_cache
    def get_mid_category(self, *, category_id: str) -> str:
        try:
            input_dto = GetMidLevelCategoryInputDTO(category_id=category_id)
        except ValidationError:
            raise InvalidCategoryID(_id=category_id)
        output_dto = get_mid_level_category(input_dto, self._repo)
        if output_dto is None:
            raise MidCategoryNotFound(_id=category_id)
        return self._generate_representation(output_dto)

    @_cache
    def get_mid_categories(self, *, parent_id: str) -> str:
        try:
            input_dto = GetMidLevelCategoriesInputDTO(parent_id=parent_id)
        except ValidationError:
            raise InvalidCategoryID(_id=parent_id)
        output_dto = get_mid_level_categories(input_dto, self._repo)
        if output_dto is None:
            raise TopCategoryNotFound(_id=parent_id)
        return self._generate_representation(output_dto)

    @_cache
    def get_terminal_category(self, *, category_id: str) -> str:
        try:
            input_dto = GetTerminalLevelCategoryInputDTO(category_id=category_id)
        except ValidationError:
            raise InvalidCategoryID(_id=category_id)
        output_dto = get_terminal_level_category(input_dto, self._repo)
        if output_dto is None:
            raise TerminalCategoryNotFound(_id=category_id)
        return self._generate_representation(output_dto)

    @_cache
    def get_terminal_categories(self, *, parent_id: str) -> str:
        try:
            input_dto = GetTerminalLevelCategoriesInputDTO(parent_id=parent_id)
        except ValidationError:
            raise InvalidCategoryID(_id=parent_id)
        output_dto = get_terminal_level_categories(input_dto, self._repo)
        if output_dto is None:
            raise MidCategoryNotFound(_id=parent_id)
        return self._generate_representation(output_dto)

    @_cache
    def get_vendor(self, *, vendor_id: str) -> str:
        try:
            input_dto = GetProductVendorInputDTO(vendor_id=vendor_id)
        except ValidationError:
            raise InvalidVendorID(_id=vendor_id)
        output_dto = get_vendor(input_dto, self._repo)
        if output_dto is None:
            raise VendorNotFound(_id=vendor_id)
        return self._generate_representation(output_dto)

    @_cache
    def get_vendors(self) -> str:
        output_dto = get_vendors(self._repo)
        return self._generate_representation(output_dto)

    @_cache
    def get_review(self, *, review_id: str) -> str:
        try:
            input_dto = GetProductReviewInputDTO(review_id=review_id)
        except ValidationError:
            raise InvalidReviewID(_id=review_id)
        output_dto = get_review(input_dto, self._repo)
        if output_dto is None:
            raise ReviewNotFound(_id=review_id)
        return self._generate_representation(output_dto)

    @_cache
    def get_reviews(self, *, product_id: str) -> str:
        try:
            input_dto = GetProductReviewsInputDTO(product_id=product_id)
        except ValidationError:
            raise InvalidProductID(_id=product_id)
        output_dto = get_reviews(input_dto, self._repo)
        if output_dto is None:
            raise ProductNotFound(_id=product_id)
        return self._generate_representation(output_dto)
