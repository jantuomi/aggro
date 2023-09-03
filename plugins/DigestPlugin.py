from typing import Any
import time

from tinydb import Query
from app.Item import Item
from app.PluginInterface import Params, PluginInterface
from app.DatabaseManager import database_manager
from app.utils import ItemDict, dict_to_item, get_param, item_to_dict


def remove_duplicates_by_key(lst: list[ItemDict], key: str) -> list[ItemDict]:
    return list({x[key]: x for x in lst}.values())


class Plugin(PluginInterface):
    def __init__(self, id: str, params: Params) -> None:
        super().__init__(id, params)
        self.digest_title = get_param("digest_title", params)
        self.digest_description = get_param("digest_description", params)
        print(f"[DigestPlugin#{self.id}] initialized")

    def item_sort_key(self, item: Item) -> time.struct_time:
        if item.pub_date is None:
            return time.localtime()

        return item.pub_date

    def make_digest(self) -> list[Item]:
        plugin_state_q = Query().plugin_id == self.id
        _d: Any = database_manager.plugin_states.get(plugin_state_q)  # type: ignore
        data: dict[str, Any] = (
            _d if _d is not None else {"plugin_id": self.id, "state": []}
        )
        state: list[ItemDict] = data["state"]
        items_to_digest = map(dict_to_item, state)

        digest_desc = (
            f"{self.digest_description}<br><br>" if self.digest_description else ""
        )

        for item in items_to_digest:
            pub_date_stamp = (
                time.strftime("%a, %d %b %Y %H:%M:%S +0000", item.pub_date)
                if item.pub_date
                else ""
            )
            author = item.author if item.author else ""
            digest_desc += f"<strong>{item.title}</strong><br>"
            digest_desc += f"<small>{pub_date_stamp} <i>{author}</i></small><br><br>"
            digest_desc += item.description if item.description else ""
            digest_desc += "<br><br>"

        digest_item: Item = Item(
            title=self.digest_title,
            description=digest_desc,
            link=None,
            author=None,
            pub_date=time.localtime(),
            category=None,
            comments=None,
            enclosures=[],
        )

        database_manager.plugin_states.upsert(  # type: ignore
            {"plugin_id": self.id, "state": []}, plugin_state_q
        )

        return [digest_item]

    def add_to_state(self, source_id: str, items: list[Item]) -> list[Item]:
        plugin_state_q = Query().plugin_id == self.id
        _d: Any = database_manager.plugin_states.get(plugin_state_q)  # type: ignore
        data: dict[str, Any] = (
            _d if _d is not None else {"plugin_id": self.id, "state": []}
        )
        state: list[ItemDict] = data["state"]

        items_as_dicts = list(map(item_to_dict, items))
        state += items_as_dicts
        state = remove_duplicates_by_key(state, "link")

        database_manager.plugin_states.upsert(  # type: ignore
            {"plugin_id": self.id, "state": state}, plugin_state_q
        )

        return []

    def process(self, source_id: str | None, items: list[Item]) -> list[Item]:
        print(f"[DigestPlugin#{self.id}] process called, n={len(items)}")
        if source_id is None:
            return self.make_digest()
        else:
            return self.add_to_state(source_id, items)
