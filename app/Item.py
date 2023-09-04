from dataclasses import dataclass
from datetime import datetime


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
    pub_date: datetime | None
    category: str | None
    comments: str | None
    enclosures: list[ItemEnclosure]
    guid: str
