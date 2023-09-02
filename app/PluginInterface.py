from abc import ABC, abstractmethod
from typing import Any

from app.Item import Item


class PluginInterface(ABC):
    def __init__(self, id: str, params: dict[str, Any]):
        self.id = id
        self.params = params

    @abstractmethod
    def process(self, source_id: str | None, items: list[Item]) -> list[Item]:
        pass
