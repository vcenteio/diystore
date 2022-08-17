from abc import ABC
from abc import abstractmethod


class Cache(ABC):
    @abstractmethod
    def get(self, **kwargs):
        ...

    @abstractmethod
    def set(self, representation: str, **kwargs):
        ...

    @abstractmethod
    def delete(self, **kwargs):
        ...
