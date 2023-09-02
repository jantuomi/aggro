from dataclasses import dataclass


@dataclass
class AggroConfig:
    server_host: str
    server_port: int
    db_path: str
    plugins: dict[str, dict[str, str]]
    graph: dict[str, list[str]]
