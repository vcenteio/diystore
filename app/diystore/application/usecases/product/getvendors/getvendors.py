from .outputdto import GetProductVendorsOutputDTO
from ..repository import ProductRepository


def get_vendors(repository: ProductRepository) -> GetProductVendorsOutputDTO:
    vendors = repository.get_vendors()
    return GetProductVendorsOutputDTO.from_entities(vendors)
