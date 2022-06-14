from uuid import UUID

import pytest
from pydantic import ValidationError

from .conftest import GetProductInputDTOFactory


def test_application_get_product_input_dto_invalid_uuid(invalid_uuid_str):
    with pytest.raises(ValidationError) as e:
        GetProductInputDTOFactory(product_id=invalid_uuid_str)
    assert e.match("uuid")


def test_application_get_product_input_dto_valid_uuid(faker):
    product_id = faker.uuid4()
    idto = GetProductInputDTOFactory(product_id=product_id)
    assert idto.product_id == UUID(product_id)
