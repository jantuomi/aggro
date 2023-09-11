from typing import Any
import bottle  # type: ignore
from tinydb import Query

from app.DatabaseManager import database_manager


def feed_id_to_td(feed_id: str) -> str:
    return f'<td><a href="/{feed_id}">{feed_id}</a></td>'


def feed_last_build_date_to_td(last_build_date: str) -> str:
    return f"<td>{last_build_date}</td>"


def feed_to_tr(feed: dict[str, str]) -> str:
    return f'<tr>{feed_id_to_td(feed["feed_id"])}{feed_last_build_date_to_td(feed.get("feed_last_build_date", ""))}</tr>'


def feeds_to_table(feeds: list[dict[str, str]]) -> str:
    if len(feeds) == 0:
        return "No feeds (yet). Add feeds by defining them in your Aggrofile. If you did that already, you might have to wait a bit for the data to propagate."

    trs: list[str] = [feed_to_tr(feed) for feed in feeds]
    thead = f"<thead><tr><td>Feed</td><td>Last build date</td></tr></thead>"
    tbody = f'<tbody>{"".join(trs)}</tbody>'
    return "<table>" + thead + tbody + "</table>"


@bottle.route("/")
def index():
    if database_manager.db is None:
        raise Exception("Database is not initialized")

    Q = Query()
    feeds = database_manager.feeds.all()

    bottle.response.set_header("content-type", "text/html")
    page = f"""
    <html lang="en">
    <head>
    <title>Aggro &ndash; Feed manipulator</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
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
    table {{
        width: 100%;
        border-collapse: collapse;
    }}

    table, th, td {{
        border: 1px solid #e0e0e0;
    }}

    th, td {{
        padding: 8px;
    }}
    </style>
    </head>
    <body>
        <h1>Aggro</h2>
        <i>Feed manipulator</i>
        <h2>Feeds served at this address</h2>
        {feeds_to_table(feeds)}
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
