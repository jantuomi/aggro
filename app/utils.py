import time
from typing import TypeAlias, Union
from app.Item import Item
from dataclasses import asdict

from app.PluginInterface import Params

ItemDictValue: TypeAlias = Union[str, dict[str, "ItemDictValue"], list["ItemDictValue"]]
ItemDict: TypeAlias = dict[str, ItemDictValue]


def get_param(key: str, params: Params) -> str:
    if key not in params:
        raise Exception(f"no {key} field in config entry: " + str(params))

    return params[key]


def item_to_dict(item: Item) -> ItemDict:
    return asdict(item)


def dict_to_item(d: ItemDict) -> Item:
    pub_date, rest = (lambda pub_date, **rest: (pub_date, rest))(**d)  # type: ignore
    return Item(pub_date=time.struct_time(pub_date), **rest)  # type: ignore
