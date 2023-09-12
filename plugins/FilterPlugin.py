from app.Item import Item
from app.PluginInterface import Params, PluginInterface
from app.utils import get_config


class Plugin(PluginInterface):
    def __init__(self, id: str, params: Params) -> None:
        super().__init__("FilterPlugin", id, params)
        self.filter_expr: str = get_config(params, "filter_expr")
        self.log("initialized")

    def process(self, source_id: str | None, items: list[Item]) -> list[Item]:
        self.log(f"filtering {len(items)} with given filter expression")
        if source_id is None:
            raise Exception(f"{self.log_prefix} can not be scheduled")

        expr = f"filter(lambda item: {self.filter_expr}, input_feed)"
        ret = list(eval(expr, {"input_feed": items}))
        self.log(f"filtering done, {len(ret)} passed filter")
        return ret
