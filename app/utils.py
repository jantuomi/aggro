from app.Item import Item


def get_param(key: str, params: dict[str, str]) -> str:
    if key not in params:
        raise Exception(f"no {key} field in config entry: " + str(params))

    return params[key]


def item_to_dict(item: Item) -> dict[str, str]:
    raise NotImplemented()


def dict_to_item(d: dict[str, str]) -> Item:
    raise NotImplemented()
