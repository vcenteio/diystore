from abc import ABC
from abc import abstractmethod


class ProductCache(ABC):
    @abstractmethod
    def get_one(self, product_id: str):
        ...

    @abstractmethod
    def get_many(self, args: dict):
        ...

    @abstractmethod
    def set_one(self, product_id: str, representation: str):
        ...

    @abstractmethod
    def set_many(self, args: dict, representation: str):
        ...

    @abstractmethod
    def del_one(self, product_id: str):
        ...

    @abstractmethod
    def del_many(self, args: dict):
        ...
