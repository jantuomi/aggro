import feedparser  # type: ignore
import time
from datetime import datetime, timezone
from typing import Any
from app.Item import Item, ItemEnclosure
from app.PluginInterface import Params, PluginInterface
from app.utils import ItemDict, get_param


def struct_time_to_utc_datetime(struct_time: time.struct_time) -> datetime:
    timestamp = time.mktime(struct_time)
    naive_datetime = datetime.fromtimestamp(timestamp)
    aware_datetime = naive_datetime.replace(tzinfo=timezone.utc)
    return aware_datetime


class Plugin(PluginInterface):
    def __init__(self, id: str, params: Params) -> None:
        super().__init__(id, params)
        self.feed_url: str = get_param("feed_url", params)

        print(f"[FeedSourcePlugin#{self.id}] initialized")

    def process(self, source_id: str | None, items: list[Item]) -> list[Item]:
        print(f"[FeedSourcePlugin#{self.id}] process called")
        if source_id is not None:
            raise Exception(
                f"FeedSourcePlugin#{self.id} can only be scheduled, trying to process items from source {source_id}"
            )

        feed: Any = feedparser.parse(self.feed_url)  # type: ignore
        result_items: list[Item] = []
        if "bozo" in feed and feed["bozo"] == 1:
            raise Exception(
                f"[FeedSourcePlugin#{self.id}] malformed XML in feed {self.feed_url}"
            )

        for _d in feed.entries:
            d: ItemDict = _d
            item_enclosures: list[ItemEnclosure] = []
            for _e in d["enclosures"]:
                e: dict[str, str] = _e  # type: ignore
                item_enclosures.append(
                    ItemEnclosure(
                        length=e["length"],
                        type=e["type"],
                        url=e["href"],
                    )
                )

            datetime_1970: datetime = datetime.fromtimestamp(0)
            published_time_struct: Any = d["published_parsed"]
            published_datetime = (
                struct_time_to_utc_datetime(published_time_struct)
                if published_time_struct
                else datetime_1970
            )

            result_items.append(
                Item(
                    title=d.get("title", None),  # type: ignore
                    link=d["link"],  # type: ignore
                    description=d.get("description", None),  # type: ignore
                    author=d.get("author", None),  # type: ignore
                    pub_date=published_datetime,
                    category=d.get("category", None),  # type: ignore
                    comments=d.get("comments"),  # type: ignore
                    enclosures=item_enclosures,
                    guid=d["link"],  # type: ignore
                )
            )

        print(
            f"[FeedSourcePlugin#{self.id}] process returns items, n={len(result_items)}"
        )
        return result_items
