import feedparser  # type: ignore
from typing import Any
from Item import Item
from PluginInterface import PluginInterface
from utils import get_param


class Plugin(PluginInterface):
    def __init__(self, id: str, params: dict[str, Any]) -> None:
        super().__init__(id, params)
        self.feed_url: str = get_param("feed_url", params)

        print(f"[FeedSourcePlugin#{self.id}] initialized")

    def validate_input_n(self, n: int) -> bool:
        return n == 0

    def process(self, inputs: list[list[Item]]) -> list[Item]:
        print(f"[FeedSourcePlugin#{self.id}] process called")
        feed: Any = feedparser.parse(self.feed_url)  # type: ignore
        items: list[Item] = []
        for d in feed.entries:
            items.append(
                Item(title=d["title"], link=d["link"], description=d["description"])
            )

        print(f"[FeedSourcePlugin#{self.id}] process returns items, n={len(items)}")
        return items
