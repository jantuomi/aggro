from abc import ABC, abstractmethod
from typing import TypeAlias

from app.Item import Item

Params: TypeAlias = dict[str, str]


class PluginInterface(ABC):
    def __init__(self, id: str, params: Params):
        self.id = id
        self.params = params

    @abstractmethod
    def process(self, source_id: str | None, items: list[Item]) -> list[Item]:
        pass
