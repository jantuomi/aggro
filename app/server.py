from typing import Any
import bottle  # type: ignore
from tinydb import Query

from app.DatabaseManager import database_manager


def feed_id_to_li(feed_id: str) -> str:
    return f'<li><a href="/{feed_id}">{feed_id}</a></li>'


def feed_ids_to_ul(feed_ids: list[str]) -> str:
    if len(feed_ids) == 0:
        return "No feeds (yet). Add feeds by defining them in your Aggrofile. If you did that already, you might have to wait a bit for the data to propagate."

    lis = [feed_id_to_li(feed_id) for feed_id in feed_ids]
    return "<ul>" + "".join(lis) + "</ul>"


@bottle.route("/")
def index():
    if database_manager.db is None:
        raise Exception("Database is not initialized")

    Q = Query()
    res = database_manager.feeds.all()
    feeds_ids = [feed["feed_id"] for feed in res]

    bottle.response.set_header("content-type", "text/html")
    page = f"""
    <html lang="en">
    <head>
    <title>Aggro &ndash; Feed manipulator</title>
    <style>
    body {{
        font-family: Open Sans, Arial;
        color: #050505;
        font-size: 16px;
        margin: 2em auto;
        max-width: 800px;
        padding: 1em;
        line-height: 1.4;
        text-align: justify;
    }}
    h1 {{
        margin-bottom: 0;
    }}
    </style>
    </head>
    <body>
        <h1>Aggro</h2>
        <i>Feed manipulator</i>
        <h2>List of feeds served at this address</h2>
        {feed_ids_to_ul(feeds_ids)}
    </body>
    </html>
    """

    return page


@bottle.route("/<feed_id>")
def feed(feed_id: str):
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
