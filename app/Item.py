from dataclasses import dataclass
import time


@dataclass
class ItemEnclosure:
    """RSS Item Enclosure object"""

    length: str
    type: str
    url: str


@dataclass
class Item:
    """RSS Item"""

    title: str | None
    link: str | None
    description: str | None
    author: str | None
    pub_date: time.struct_time | None
    category: str | None
    comments: str | None
    enclosures: list[ItemEnclosure]
