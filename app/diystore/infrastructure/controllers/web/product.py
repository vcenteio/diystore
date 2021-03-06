from typing import Optional

from pydantic import ValidationError

from .exceptions import UnprocessableEntity
from .exceptions import InvalidQueryArgument
from .exceptions import InvalidProductID
from .exceptions import ProductNotFound
from ..presenters import generate_json_presentation
from ...repositories.sqlrepository import SQLProductRepository
from ...settings import InfraSettings
from ....application.usecases.product import get_product_use_case
from ....application.usecases.product import get_products_use_case
from ....application.usecases.product import GetProductInputDTO
from ....application.usecases.product import GetProductsInputDTO
from ....application.usecases.product import ProductOrderingCriteria
from ....application.usecases.product import OrderingProperty
from ....application.usecases.product import OrderingType
from ....application.dto import DTO
from ...repositories.sqlrepository import ProductOrmModel


class ProductController:

    _repo_map = {"sql": SQLProductRepository}
    _presenter_map = {"json": generate_json_presentation}

    def __init__(self, settings: InfraSettings = InfraSettings()):
        self._settings = settings
        self._configure_repository()
        self._configure_presenter()

    def _configure_repository(self):
        try:
            repo = self._repo_map.get(self._settings.repo.type)
            self._repo = repo(db_url=self._settings.repo.db_url)
        except KeyError:
            raise ValueError(
                f"unknown repository type setting: {self._settings.repo.type}"
            )

    def _configure_presenter(self):
        try:
            self._presenter = self._presenter_map.get(self._settings.presentation_type)
        except KeyError:
            raise ValueError(
                f"unknown presentation type {self._settings.presentation_type}"
            )

    def _generate_presentation(self, output_dto: DTO) -> str:
        return self._presenter(output_dto)

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

    def get_many(
        self,
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
