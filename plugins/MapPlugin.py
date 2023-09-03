from dataclasses import fields
from typing import Any
from app.Item import Item
from app.PluginInterface import Params, PluginInterface
from app.utils import get_param


def set_field(item: Item, k: str, v: Any):
    field_names = [f.name for f in fields(Item)]
    if k not in field_names:
        raise Exception(f"Invalid set_field key: {k}")

    setattr(item, k, v)
    return item


class Plugin(PluginInterface):
    def __init__(self, id: str, params: Params) -> None:
        super().__init__(id, params)
        self.map_expr: str = get_param("map_expr", params)
        print(f"[MapItemPlugin#{self.id}] initialized")

    def process(self, source_id: str | None, items: list[Item]) -> list[Item]:
        print(f"[MapItemPlugin#{self.id}] process called, n={len(items)}")
        if source_id is None:
            raise Exception(f"[MapItemPlugin#{self.id}] can not be scheduled")

        expr = f"map(lambda item: {self.map_expr}, input_feed)"
        ret = list(eval(expr, {"input_feed": items, "set_field": set_field}))
        print(f"[MapItemPlugin#{self.id}] process returning items, n={len(ret)}")
        return ret
