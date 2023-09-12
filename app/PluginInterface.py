from abc import ABC, abstractmethod
from typing import TypeAlias

from app.Item import Item

Params: TypeAlias = dict[str, str]


class PluginInterface(ABC):
    name: str

    def __init__(self, plugin_type: str, id: str, params: Params):
        self.plugin_type = plugin_type
        self.id = id
        self.params = params
        self.log_prefix = f"[{self.plugin_type}#{self.id}]"

    def log(self, msg) -> None:
        print(f"{self.log_prefix} {msg}")

    @abstractmethod
    def process(self, source_id: str | None, items: list[Item]) -> list[Item]:
        return NotImplemented
