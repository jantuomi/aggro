from typing import Any
from app.Item import Item
from app.PluginInterface import PluginInterface
from app.utils import get_param
import xml.etree.ElementTree as ET


# <?xml version="1.0" encoding="UTF-8" ?>
# <rss version="2.0">

# <channel>
#   <title>W3Schools Home Page</title>
#   <link>https://www.w3schools.com</link>
#   <description>Free web building tutorials</description>
#   <item>
#     <title>RSS Tutorial</title>
#     <link>https://www.w3schools.com/xml/xml_rss.asp</link>
#     <description>New RSS tutorial on W3Schools</description>
#   </item>
#   <item>
#     <title>XML Tutorial</title>
#     <link>https://www.w3schools.com/xml</link>
#     <description>New XML tutorial on W3Schools</description>
#   </item>
# </channel>

# </rss>


class Plugin(PluginInterface):
    def __init__(self, id: str, params: dict[str, Any]) -> None:
        super().__init__(id, params)
        self.feed_name: str = get_param("feed_name", params)
        print(f"[FeedSinkPlugin#{self.id}] initialized")

    def build_xml(self, items: list[Item]):
        rss = ET.Element("rss", {"version": "2.0"})
        channel = ET.SubElement(rss, "channel")
        title = ET.SubElement(channel, "title")
        title.text = "channel title"
        link = ET.SubElement(channel, "link")
        link.text = "channel link"
        description = ET.SubElement(channel, "description")
        description.text = "channel description"

        for item in items:
            item_elem = ET.SubElement(channel, "item")
            item_title = ET.SubElement(item_elem, "title")
            item_title.text = item.title
            item_link = ET.SubElement(item_elem, "link")
            item_link.text = item.link
            item_description = ET.SubElement(item_elem, "description")
            item_description.text = item.description

        return ET.tostring(rss, "unicode")

    def process(self, source_id: str | None, items: list[Item]) -> list[Item]:
        print(f"[FeedSinkPlugin#{self.id}] process called, n={len(items)}")
        if source_id is None:
            raise Exception(f"FeedSinkPlugin#{self.id} can not be scheduled")

        ret = self.build_xml(items)
        print(f"[FeedSinkPlugin#{self.id}] process returning XML:")
        print(ret)
        return []
