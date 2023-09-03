from typing import Any

from tinydb import Query
from app.Item import Item
from app.PluginInterface import PluginInterface
from app.DatabaseManager import database_manager
from app.utils import dict_to_item, item_to_dict

# TODO


class Plugin(PluginInterface):
    def __init__(self, id: str, params: dict[str, Any]) -> None:
        super().__init__(id, params)
        print(f"[ConcatPlugin#{self.id}] initialized")

    def process(self, source_id: str | None, items: list[Item]) -> list[Item]:
        print(f"[ConcatPlugin#{self.id}] process called, n={len(items)}")
        if source_id is None:
            raise Exception(f"[ConcatPlugin#{self.id}] can not be scheduled")

        Q = Query()
        q_result = database_manager.plugin_states.search(Q.plugin_id == self.id)
        if len(q_result) > 1:
            raise Exception(
                f"[ConcatPlugin#{self.id}] invalid database state, found more than 1 plugin state: {len(q_result)}"
            )

        d: Any = q_result[0] if len(q_result) == 1 else {}
        data: dict[str, list[dict[str, str]]] = d

        if source_id in data:
            items_as_dicts = list(map(item_to_dict, items))
            d[source_id] = items_as_dicts

        aggregated_item_dicts: list[dict[str, str]] = []
        for data_source_id in data:
            item_dicts = data[data_source_id]
            aggregated_item_dicts += item_dicts

        ret = list(map(dict_to_item, aggregated_item_dicts))

        print(f"[ConcatPlugin#{self.id}] process returning items, n={len(ret)}")
        return ret
