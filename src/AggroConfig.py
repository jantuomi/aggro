from dataclasses import dataclass


@dataclass
class AggroConfig:
    plugins: dict[str, dict[str, str]]
    graph: dict[str, list[str]]
