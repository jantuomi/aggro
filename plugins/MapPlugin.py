from dataclasses import fields
from typing import Any
from app.Item import Item
from app.PluginInterface import Params, PluginInterface
from app.utils import get_config


def set_field(item: Item, k: str, v: Any):
    field_names = [f.name for f in fields(Item)]
    if k not in field_names:
        raise Exception(f"Invalid set_field key: {k}")

    setattr(item, k, v)
    return item


class Plugin(PluginInterface):
    def __init__(self, id: str, params: Params) -> None:
        super().__init__("MapPlugin", id, params)
        self.map_expr: str = get_config(params, "map_expr")
        self.log("initialized")

    def process(self, source_id: str | None, items: list[Item]) -> list[Item]:
        if source_id is None:
            raise Exception(f"{self.log_prefix} can not be scheduled")

        self.log(f"mapping over {len(items)} posts with given map expression")

        expr = f"map(lambda item: {self.map_expr}, input_feed)"
        ret = list(eval(expr, {"input_feed": items, "set_field": set_field}))
        self.log(f"mapped over {len(ret)} posts")
        return ret
