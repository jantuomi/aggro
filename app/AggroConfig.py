from dataclasses import dataclass

from app.PluginInterface import Params


@dataclass
class AggroConfigServer:
    host: str
    port: int


@dataclass
class AggroConfigEmailAlerter:
    api_url: str
    api_headers: dict[str, str]
    email_from: str
    email_to: list[str]


@dataclass
class AggroConfig:
    server: AggroConfigServer
    email_alerter: AggroConfigEmailAlerter | None
    db_path: str
    plugins: dict[str, Params]
    graph: dict[str, list[str]]
