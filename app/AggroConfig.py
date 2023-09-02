from dataclasses import dataclass


@dataclass
class AggroConfig:
    db_path: str
    plugins: dict[str, dict[str, str]]
    graph: dict[str, list[str]]
