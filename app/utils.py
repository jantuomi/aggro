def get_param(key: str, params: dict[str, str]) -> str:
    if key not in params:
        raise Exception(f"no {key} field in config entry: " + str(params))

    return params[key]
