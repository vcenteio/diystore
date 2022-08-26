from decimal import Decimal

from factory import Factory
from factory import SubFactory
from factory import Faker

from diystore.application.usecases.product import GetProductsInputDTO
from diystore.application.usecases.product import ProductOrderingCriteria
from diystore.application.usecases.product import GetProductOutputDTO
from diystore.application.usecases.product import GetProductInputDTO


class ProductOrderingCriteriaStub(Factory):
    class Meta:
        model = ProductOrderingCriteria

    property = Faker("random_element", elements=(1, 2))
    type = Faker("random_element", elements=(1, 2))


class GetProductsInputDTOStub(Factory):
    class Meta:
        model = GetProductsInputDTO

    category_id = Faker("uuid4")
    price_min = Faker("pydecimal", min_value=0, max_value=99, right_digits=2)
    price_max = Faker("pydecimal", min_value=100, max_value=999, right_digits=2)
    rating_min = Faker("pydecimal", min_value=0, max_value=2, right_digits=1)
    rating_max = Faker("pydecimal", min_value=3, max_value=5, right_digits=1)
    ordering_criteria = SubFactory(ProductOrderingCriteriaStub)
    with_discounts_only = Faker("pybool")


class GetProductOutputDTOStub(Factory):
    class Meta:
        model = GetProductOutputDTO

    id = Faker("uuid4")
    ean = Faker("bothify", text="#############")
    name = Faker("word")
    description = Faker("pystr", min_chars=1, max_chars=300)
    price: Decimal = Faker("pyfloat", right_digits=2, min_value=0.01, max_value=999.99)
    discount: Decimal = Faker(
        "pyfloat", right_digits=2, min_value=0.1, max_value=1, positive=True
    )
    price_without_discount: Decimal = Faker(
        "pyfloat", right_digits=2, min_value=0.01, max_value=999.99
    )
    base_price: Decimal = Faker(
        "pyfloat", right_digits=2, min_value=0.01, max_value=999.99
    )
    vat: Decimal = Faker("pyfloat", right_digits=2, min_value=0, max_value=1)
    in_stock: bool = Faker("pybool")
    rating: Decimal = Faker("pyfloat", right_digits=1, min_value=0, max_value=5)
    height: Decimal = Faker("pyfloat", right_digits=1, min_value=1, max_value=99.9)
    width: Decimal = Faker("pyfloat", right_digits=1, min_value=1, max_value=99.9)
    length: Decimal = Faker("pyfloat", right_digits=1, min_value=1, max_value=99.9)
    color = Faker("color_name")
    material = Faker("word")
    country_of_origin = Faker("country")
    warranty = Faker("pyint", min_value=0, max_value=5)
    category_id = Faker("uuid4")
    category_name = Faker("word")
    client_rating = Faker(
        "pydecimal", right_digits=1, min_value=Decimal("0"), max_value=Decimal("5")
    )
    thumbnail_photo_url = Faker("image_url")
    medium_size_photo_url = Faker("image_url")
    large_size_photo_url = Faker("image_url")
    vendor_id = Faker("uuid4")
    vendor_name = Faker("word")


class GetProductInputDTOStub(Factory):
    class Meta:
        model = GetProductInputDTO

    product_id = Faker("uuid4")
