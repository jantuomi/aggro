from dataclasses import dataclass

from app.PluginInterface import Params


@dataclass
class AggroConfig:
    server_host: str
    server_port: int
    db_path: str
    plugins: dict[str, Params]
    graph: dict[str, list[str]]
