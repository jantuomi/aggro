from dataclasses import dataclass
from datetime import datetime
from typing import Literal


@dataclass
class ItemEnclosure:
    """RSS Item Enclosure object"""

    length: str
    type: str
    url: str


@dataclass
class ItemGUID:
    """RSS Item GUID object"""

    value: str
    is_perma_link: bool = False


@dataclass
class ItemMediaContent:
    """RSS Item media:content object"""

    url: str
    medium: Literal["video", "image"]


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
    guid: ItemGUID
    media_content: ItemMediaContent | None
