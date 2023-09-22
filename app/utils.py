import os
from datetime import datetime
from typing import Any, TypeAlias, Union
from app.Item import Item
from dataclasses import asdict

ItemDictValue: TypeAlias = Union[str, dict[str, "ItemDictValue"], list["ItemDictValue"]]
ItemDict: TypeAlias = dict[str, ItemDictValue]


def evaluate_env_ref(v: Any) -> str:
    if type(v) == str and v.startswith("${") and v.endswith("}"):
        return os.environ[v[2:-1]]
    else:
        return v


def get_config(config: dict[str, Any], key: str) -> Any:
    v: Any
    try:
        v = config[key]
    except KeyError:
        raise Exception(f"no {key} field in config: " + str(config))

    if type(v) == list:
        mapped = map(evaluate_env_ref, v)
        return list(mapped)
    else:
        return evaluate_env_ref(v)


def get_config_or_default(
    config: dict[str, Any], key: str, default: Any | None = None
) -> Any:
    v: Any = config.get(key, default)

    if type(v) == list:
        mapped = map(evaluate_env_ref, v)
        return list(mapped)
    else:
        return evaluate_env_ref(v)


def item_to_dict(item: Item) -> ItemDict:
    d = asdict(item)
    d["pub_date"] = datetime.isoformat(d["pub_date"]) if d["pub_date"] else None
    return d


def dict_to_item(d: ItemDict) -> Item:
    pub_date, rest = (lambda pub_date, **rest: (pub_date, rest))(**d)  # type: ignore
    return Item(pub_date=datetime.fromisoformat(pub_date), **rest)  # type: ignore
