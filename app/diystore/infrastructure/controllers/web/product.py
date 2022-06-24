from typing import Optional

from pydantic import ValidationError

from .exceptions import InvalidProductID
from .exceptions import ProductNotFound
from ..presenters import generate_json_presentation
from ...repositories.sqlrepository import SQLProductRepository
from ...settings import InfraSettings
from ....application.usecases.product import get_product_use_case
from ....application.usecases.product import get_products_use_case
from ....application.usecases.product import GetProductInputDTO
from ....application.usecases.product import GetProductsInputDTO
from ....application.dto import DTO


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
