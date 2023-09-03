from typing import Any
import time

from tinydb import Query
from app.Item import Item
from app.PluginInterface import Params, PluginInterface
from app.DatabaseManager import database_manager
from app.utils import ItemDict, dict_to_item, item_to_dict


class Plugin(PluginInterface):
    def __init__(self, id: str, params: Params) -> None:
        super().__init__(id, params)
        print(f"[ConcatPlugin#{self.id}] initialized")

    def item_sort_key(self, item: Item) -> time.struct_time:
        if item.pub_date is None:
            return time.localtime()

        return item.pub_date

    def process(self, source_id: str | None, items: list[Item]) -> list[Item]:
        print(f"[ConcatPlugin#{self.id}] process called, n={len(items)}")
        if source_id is None:
            raise Exception(f"[ConcatPlugin#{self.id}] can not be scheduled")

        plugin_state_q = Query().plugin_id == self.id
        _d: Any = database_manager.plugin_states.get(plugin_state_q)  # type: ignore
        data: dict[str, Any] = (
            _d if _d is not None else {"plugin_id": self.id, "state": {}}
        )
        state = data["state"]

        items_as_dicts = list(map(item_to_dict, items))
        state[source_id] = items_as_dicts

        database_manager.plugin_states.upsert(  # type: ignore
            {"plugin_id": self.id, "state": state}, plugin_state_q
        )

        aggregated_item_dicts: list[ItemDict] = []
        for data_source_id in state:
            item_dicts = state[data_source_id]
            aggregated_item_dicts += item_dicts

        ret_items = list(map(dict_to_item, aggregated_item_dicts))
        ret = sorted(ret_items, key=self.item_sort_key)

        print(f"[ConcatPlugin#{self.id}] process returning items, n={len(ret)}")
        return ret
