import feedparser  # type: ignore
import time
from datetime import datetime, timezone
from typing import Any
from app.Item import Item, ItemEnclosure, ItemGUID, ItemMediaContent
from app.PluginInterface import Params, PluginInterface
from app.utils import ItemDict, get_config


def struct_time_to_utc_datetime(struct_time: time.struct_time) -> datetime:
    timestamp = time.mktime(struct_time)
    naive_datetime = datetime.fromtimestamp(timestamp)
    aware_datetime = naive_datetime.replace(tzinfo=timezone.utc)
    return aware_datetime


class Plugin(PluginInterface):
    def __init__(self, id: str, params: Params) -> None:
        super().__init__("FeedSourcePlugin", id, params)
        self.feed_url: str = get_config(params, "feed_url")

        self.log("initialized")

    def process(self, source_id: str | None, items: list[Item]) -> list[Item]:
        if source_id is not None:
            raise Exception(
                f"FeedSourcePlugin#{self.id} can only be scheduled, trying to process items from source {source_id}"
            )

        self.log(f'fetching feed "{self.feed_url}"')
        feed: Any = feedparser.parse(self.feed_url)  # type: ignore
        result_items: list[Item] = []
        if "bozo" in feed and feed["bozo"] == 1:
            raise Exception(f"{self.log_prefix} malformed XML in feed {self.feed_url}")

        if "image" in feed:
            image_url = feed["image"]["href"]
            media_content = ItemMediaContent(
                url=image_url,
                medium="image",
            )
        else:
            media_content = None

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

            link: str = d["link"]  # type: ignore

            result_items.append(
                Item(
                    title=d.get("title", None),  # type: ignore
                    link=link,
                    description=d.get("description", None),  # type: ignore
                    author=d.get("author", None),  # type: ignore
                    pub_date=published_datetime,
                    category=d.get("category", None),  # type: ignore
                    comments=d.get("comments"),  # type: ignore
                    enclosures=item_enclosures,
                    guid=ItemGUID(link, is_perma_link=True),
                    media_content=media_content,
                )
            )

        print(
            f'{self.log_prefix} fetched {len(result_items)} from the feed "{self.feed_url}"'
        )
        return result_items
