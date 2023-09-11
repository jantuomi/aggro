from typing import Any
import xml.etree.ElementTree as ET

from tinydb import Query

from app.Item import Item
from app.PluginInterface import PluginInterface
from app.utils import get_config, get_config_or_default
from app.DatabaseManager import database_manager


class Plugin(PluginInterface):
    def __init__(self, id: str, params: dict[str, Any]) -> None:
        super().__init__(id, params)
        self.feed_id: str = get_config(params, "feed_id")
        self.feed_title: str = get_config(params, "feed_title")
        self.feed_link: str | None = get_config_or_default(params, "feed_link", None)
        self.feed_description: str = get_config(params, "feed_description")
        print(f"[FeedSinkPlugin#{self.id}] initialized")
        print(f"[FeedSinkPlugin#{self.id}] feed will be served at path /{self.feed_id}")

    def build_xml(self, items: list[Item]):
        rss = ET.Element("rss", {"version": "2.0"})
        channel = ET.SubElement(rss, "channel")
        title = ET.SubElement(channel, "title")
        title.text = self.feed_title
        if self.feed_link is not None:
            link = ET.SubElement(channel, "link")
            link.text = self.feed_link
        description = ET.SubElement(channel, "description")
        description.text = self.feed_description

        for item in items:
            item_elem = ET.SubElement(channel, "item")
            if item.title is not None:
                item_title = ET.SubElement(item_elem, "title")
                item_title.text = item.title
            if item.link is not None:
                item_link = ET.SubElement(item_elem, "link")
                item_link.text = item.link
            if item.description is not None:
                item_description = ET.SubElement(item_elem, "description")
                item_description.text = item.description
            if item.category is not None:
                item_category = ET.SubElement(item_elem, "category")
                item_category.text = item.category
            if item.comments is not None:
                item_comments = ET.SubElement(item_elem, "comments")
                item_comments.text = item.comments
            if item.pub_date is not None:
                item_pub_date = ET.SubElement(item_elem, "pubDate")
                item_pub_date.text = item.pub_date.strftime(
                    "%a, %d %b %Y %H:%M:%S +0000"
                )
            if item.author is not None:
                item_author = ET.SubElement(item_elem, "author")
                item_author.text = item.author

            item_guid = ET.SubElement(
                item_elem,
                "guid",
                {"isPermaLink": "true" if item.guid.is_perma_link else "false"},
            )
            item_guid.text = item.guid.value

            for enc in item.enclosures:
                ET.SubElement(
                    item_elem,
                    "enclosure",
                    {
                        "length": enc.length,
                        "type": enc.type,
                        "url": enc.url,
                    },
                )

        return ET.tostring(rss, "unicode")

    def process(self, source_id: str | None, items: list[Item]) -> list[Item]:
        print(f"[FeedSinkPlugin#{self.id}] process called, n={len(items)}")

        if source_id is None:
            raise Exception(f"FeedSinkPlugin#{self.id} can not be scheduled")
        if database_manager.db is None:
            raise Exception("Database is not initialized")

        ret = self.build_xml(items)

        Q = Query()
        database_manager.feeds.upsert({"feed_id": self.feed_id, "feed_xml": ret}, Q.feed_id == self.feed_id)  # type: ignore
        print(f"[FeedSinkPlugin#{self.id}] processed")
        return []
