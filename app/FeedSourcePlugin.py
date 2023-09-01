import feedparser  # type: ignore
from typing import Any
from app.Item import Item
from app.PluginInterface import PluginInterface
from app.utils import get_param


class Plugin(PluginInterface):
    def __init__(self, id: str, params: dict[str, Any]) -> None:
        super().__init__(id, params)
        self.feed_url: str = get_param("feed_url", params)

        print(f"[FeedSourcePlugin#{self.id}] initialized")

    def process(self, items: list[Item]) -> list[Item]:
        print(f"[FeedSourcePlugin#{self.id}] process called")
        feed: Any = feedparser.parse(self.feed_url)  # type: ignore
        result_items: list[Item] = []
        if "bozo" in feed and feed["bozo"] == 1:
            raise Exception(
                f"[FeedSourcePlugin#{self.id}] malformed XML in feed {self.feed_url}"
            )

        for d in feed.entries:
            result_items.append(
                Item(title=d["title"], link=d["link"], description=d["description"])
            )

        print(f"[FeedSourcePlugin#{self.id}] process returns items, n={len(items)}")
        return result_items
