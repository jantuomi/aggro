from typing import Any
from app.Item import Item
from app.PluginInterface import PluginInterface
from app.utils import get_param


class Plugin(PluginInterface):
    def __init__(self, id: str, params: dict[str, Any]) -> None:
        super().__init__(id, params)
        self.filter_expr: str = get_param("filter_expr", params)
        print(f"[FilterPlugin#{self.id}] initialized")

    def process(self, items: list[Item]) -> list[Item]:
        print(f"[FilterPlugin#{self.id}] process called, n={len(items)}")
        expr = f"filter(lambda item: {self.filter_expr}, input_feed)"
        ret = list(eval(expr, {"input_feed": items}))
        print(f"[FilterPlugin#{self.id}] process returning items, n={len(ret)}")
        return ret
