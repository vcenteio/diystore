from abc import ABC


class DTO(ABC):
    def json(self) -> str:
        ...

    def dict(self) -> dict:
        ...
