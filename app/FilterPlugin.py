from typing import Any
from app.Item import Item
from app.PluginInterface import PluginInterface
from app.utils import get_param


class Plugin(PluginInterface):
    def __init__(self, id: str, params: dict[str, Any]) -> None:
        super().__init__(id, params)
        self.filter_expr: str = get_param("filter_expr", params)
        print(f"[FilterPlugin#{self.id}] initialized")

    def validate_input_n(self, n: int) -> bool:
        return n == 1

    def process(self, inputs: list[list[Item]]) -> list[Item]:
        input_feed: list[Item] = inputs[0]
        print(f"[FilterPlugin#{self.id}] process called, n={len(input_feed)}")
        expr = f"filter(lambda item: {self.filter_expr}, input_feed)"
        ret = list(eval(expr, {"input_feed": input_feed}))
        print(f"[FilterPlugin#{self.id}] process returning items, n={len(ret)}")
        return ret
