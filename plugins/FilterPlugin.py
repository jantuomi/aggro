from app.Item import Item
from app.PluginInterface import Params, PluginInterface
from app.utils import get_param


class Plugin(PluginInterface):
    def __init__(self, id: str, params: Params) -> None:
        super().__init__(id, params)
        self.filter_expr: str = get_param("filter_expr", params)
        print(f"[FilterPlugin#{self.id}] initialized")

    def process(self, source_id: str | None, items: list[Item]) -> list[Item]:
        print(f"[FilterPlugin#{self.id}] process called, n={len(items)}")
        if source_id is None:
            raise Exception(f"[FilterPlugin#{self.id}] can not be scheduled")

        expr = f"filter(lambda item: {self.filter_expr}, input_feed)"
        ret = list(eval(expr, {"input_feed": items}))
        print(f"[FilterPlugin#{self.id}] process returning items, n={len(ret)}")
        return ret
