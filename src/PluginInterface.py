from abc import ABC, abstractmethod
from typing import Any

from Item import Item


class PluginInterface(ABC):
    def __init__(self, id: str, params: dict[str, Any]):
        self.id = id
        self.params = params

    @abstractmethod
    def validate_input_n(self, n: int) -> bool:
        raise NotImplemented("abstract method not implemented")

    @abstractmethod
    def process(self, inputs: list[list[Item]]) -> list[Item]:
        pass
