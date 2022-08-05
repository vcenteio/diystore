from abc import ABC
from typing import Callable


class IoCContainer:
    def __init__(self):
        self._class_bindings = {}
        self._function_bindings = {}

    def register(self, interface: ABC, implementation: object, **kwargs: dict):
        self._class_bindings[interface] = (implementation, kwargs)

    def provide(self, interface: ABC) -> object:
        implementation, kwargs = self._class_bindings[interface]
        return implementation(**kwargs)

    def register_function(self, _type: str, _function: Callable):
        self._function_bindings[_type] = _function

    def provide_function(self, _type: str) -> Callable:
        return self._function_bindings[_type]
