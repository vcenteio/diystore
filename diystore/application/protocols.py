from typing import Protocol


class DictExportable(Protocol):
    def dict(self) -> dict:
        ...
