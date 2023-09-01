from dataclasses import dataclass


@dataclass
class Item:
    """RSS Item"""

    title: str
    link: str
    description: str
