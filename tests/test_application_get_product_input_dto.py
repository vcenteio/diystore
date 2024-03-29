from uuid import UUID

import pytest
from pydantic import ValidationError

from diystore.application.usecases.product.stubs import GetProductInputDTOStub


def test_application_get_product_input_dto_invalid_uuid(invalid_uuid_str):
    with pytest.raises(ValidationError) as e:
        GetProductInputDTOStub(product_id=invalid_uuid_str)
    assert e.match("uuid")


def test_application_get_product_input_dto_valid_uuid(faker):
    product_id = faker.uuid4()
    idto = GetProductInputDTOStub(product_id=product_id)
    assert idto.product_id == UUID(product_id)
