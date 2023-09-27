from dataclasses import dataclass

from app.PluginInterface import Params


@dataclass
class AggroConfigServer:
    host: str
    port: int


@dataclass
class AggroConfigSendGridAlerter:
    api_token: str
    email_from: str
    email_to: list[str]


@dataclass
class AggroConfig:
    server: AggroConfigServer
    sendgrid_alerter: AggroConfigSendGridAlerter | None
    db_path: str
    plugins: dict[str, Params]
    graph: dict[str, list[str]]
