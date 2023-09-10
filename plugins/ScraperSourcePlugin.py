from bs4 import BeautifulSoup
import feedparser  # type: ignore
import time
from datetime import datetime, timezone
from typing import Any

import requests
from app.Item import Item, ItemEnclosure
from app.PluginInterface import Params, PluginInterface
from app.utils import ItemDict, get_config, get_config_or_default


def struct_time_to_utc_datetime(struct_time: time.struct_time) -> datetime:
    timestamp = time.mktime(struct_time)
    naive_datetime = datetime.fromtimestamp(timestamp)
    aware_datetime = naive_datetime.replace(tzinfo=timezone.utc)
    return aware_datetime


class Plugin(PluginInterface):
    def __init__(self, id: str, params: Params) -> None:
        super().__init__(id, params)
        self.url: str = get_config(params, "url")
        self.selector_post: str = get_config(params, "selector_post")
        self.selector_title: str | None = get_config_or_default(
            params, "selector_title", None
        )
        self.selector_date: str | None = get_config_or_default(
            params, "selector_date", None
        )
        self.selector_link: str | None = get_config_or_default(
            params, "selector_link", None
        )
        self.selector_description: str | None = get_config_or_default(
            params, "selector_description", None
        )
        self.selector_author: str | None = get_config_or_default(
            params, "selector_author", None
        )

        print(f"[ScraperSourcePlugin#{self.id}] initialized")

    def process(self, source_id: str | None, items: list[Item]) -> list[Item]:
        print(f"[ScraperSourcePlugin#{self.id}] process called")

        result_items: list[Item] = []
        with requests.session() as session:
            page_resp = session.get(self.url, allow_redirects=True)
            page_elem = BeautifulSoup(page_resp.text, features="lxml")
            post_elems = eval(self.selector_post, {"page": page_elem})

            for post_elem in post_elems:
                if self.selector_link:
                    link_elem = eval(
                        self.selector_link, {"page": page_elem, "post": post_elem}
                    )[0]
                    detail_page_url = link_elem["href"]
                    if detail_page_url.startswith("/"):
                        detail_page_url = self.url.strip("/") + detail_page_url
                else:
                    detail_page_url = None

                if detail_page_url:
                    detail_page_resp = session.get(
                        detail_page_url, allow_redirects=True
                    )
                    detail_page_elem = BeautifulSoup(
                        detail_page_resp.text, features="lxml"
                    )
                    guid = detail_page_url
                else:
                    detail_page_elem = None
                    guid = None

                if self.selector_title:
                    title_elem = eval(
                        self.selector_title,
                        {
                            "page": page_elem,
                            "post": post_elem,
                            "detail_page": detail_page_elem,
                        },
                    )[0]
                    title = title_elem.get_text().strip()
                else:
                    title = None

                if self.selector_description:
                    description_elem = eval(
                        self.selector_description,
                        {
                            "page": page_elem,
                            "post": post_elem,
                            "detail_page": detail_page_elem,
                        },
                    )[0]
                    description = str(description_elem).strip()
                else:
                    description = None

                if self.selector_date:
                    date_elem = eval(
                        self.selector_date,
                        {
                            "page": page_elem,
                            "post": post_elem,
                            "detail_page": detail_page_elem,
                        },
                    )[0]
                    date = date_elem.get_text().strip()
                else:
                    date = None

                if self.selector_author:
                    author_elem = eval(
                        self.selector_author,
                        {
                            "page": page_elem,
                            "post": post_elem,
                            "detail_page": detail_page_elem,
                        },
                    )[0]
                    author = author_elem.get_text().strip()
                else:
                    author = None

                if guid is None:
                    guid = f"aggro__{self.id}__{title}"

                item = Item(
                    title=f"{date} – {title}",
                    link=detail_page_url,
                    description=description,
                    pub_date=datetime.now(),
                    author=author,
                    category=None,
                    comments=None,
                    enclosures=[],
                    guid=guid,
                )
                result_items.append(item)

        print(
            f"[ScraperSourcePlugin#{self.id}] process returns items, n={len(result_items)}"
        )
        return result_items
