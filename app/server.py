from typing import Any
import bottle as _bottle  # type: ignore
from tinydb import Query

from app.DatabaseManager import database_manager

bottle: Any = _bottle


@bottle.route("/<feed_id>")
def index(feed_id: str):
    if database_manager.db is None:
        raise Exception("Database is not initialized")

    Q = Query()
    res = database_manager.feeds.search(Q.feed_id == feed_id)
    if len(res) == 0:
        bottle.abort(400, f"No feed found with id {feed_id}")

    if len(res) > 1:
        bottle.abort(400, f"Weird number of feeds found with id {feed_id}: {len(res)}")

    bottle.response.set_header("content-type", "application/xml")

    feed: Any = res[0]  # type: ignore
    feed_xml: str = feed["feed_xml"]
    return feed_xml


def run_web_server(host: str, port: int):
    bottle.run(host=host, port=port)
