from typing import Optional

from .inputdto import GetProductVendorInputDTO
from .outputdto import GetProductVendorOutputDTO
from ..repository import ProductRepository
from .....domain.entities.product.vendor import ProductVendor


def get_vendor(
    input_dto: GetProductVendorInputDTO, repository: ProductRepository
) -> Optional[ProductVendor]:
    vendor = repository.get_vendor(input_dto.vendor_id)
    if vendor is not None:
        return GetProductVendorOutputDTO.from_entity(vendor)
    return None
