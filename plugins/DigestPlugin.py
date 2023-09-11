from dataclasses import dataclass
from typing import Any
from datetime import datetime, timedelta
import re

from tinydb import Query
from app.Item import Item, ItemGUID
from app.PluginInterface import Params, PluginInterface
from app.DatabaseManager import database_manager
from app.utils import dict_to_item, get_config_or_default, item_to_dict, get_config


def add_days(start: datetime, days: int):
    return start + timedelta(days=days)


def add_weeks(start: datetime, weeks: int):
    return start + timedelta(weeks=weeks)


def add_months(start: datetime, months: int):
    year, month = divmod(start.month - 1 + months, 12)
    return datetime(
        year=start.year + year, month=month + 1, day=start.day, tzinfo=start.tzinfo
    )


def add_years(start: datetime, years: int):
    return datetime(
        year=start.year + years, month=start.month, day=start.day, tzinfo=start.tzinfo
    )


add_interval_map = {"d": add_days, "w": add_weeks, "m": add_months, "y": add_years}


@dataclass
class Span:
    span_title: str
    items: list[Item]


def group_by_time_span(
    lst: list[Item], interval: tuple[int, str], start_datetime: datetime
) -> list[Span]:
    interval_n, interval_suffix = interval
    datetime_1970: datetime = datetime.fromtimestamp(0)
    sorted_lst = sorted(
        lst,
        key=lambda item: item.pub_date if item.pub_date else datetime_1970,
    )

    groups: list[Span] = []
    start = start_datetime
    end = add_interval_map[interval_suffix](start, interval_n)
    group: list[Item] = []
    for item in sorted_lst:
        item_datetime = item.pub_date if item.pub_date else datetime_1970
        while item_datetime >= end:
            if group:
                formatted_start = start.strftime("%Y-%m-%d")
                formatted_end = end.strftime("%Y-%m-%d")
                groups.append(
                    Span(
                        span_title=f"{formatted_start} to {formatted_end}", items=group
                    )
                )
                group = []
            start = end
            end = add_interval_map[interval_suffix](start, interval_n)

        if start <= item_datetime < end:
            group.append(item)

    if group:
        formatted_start = start.strftime("%Y-%m-%d")
        formatted_end = end.strftime("%Y-%m-%d")
        groups.append(
            Span(span_title=f"{formatted_start} to {formatted_end}", items=group)
        )

    return groups


def parse_interval(interval: str) -> tuple[int, str]:
    # Parse the interval string into a number and a suffix
    match = re.match(r"(\d+)([dwmy])", interval)
    if not match:
        raise ValueError(
            'Invalid interval format. Must be a number followed by one of "d", "w", "m", or "y".'
        )

    num, suffix = match.groups()
    num = int(num)

    return (num, suffix)


class Plugin(PluginInterface):
    def __init__(self, id: str, params: Params) -> None:
        super().__init__(id, params)
        self.digest_title_prefix = get_config(params, "digest_title_prefix")
        self.digest_description = get_config_or_default(
            params, "digest_description", None
        )
        self.digest_link = get_config_or_default(params, "digest_link", None)
        from_datatime_str = get_config(params, "from_datetime")
        self.from_datetime = datetime.fromisoformat(from_datatime_str)
        interval = get_config(params, "interval")
        self.interval_pair = parse_interval(interval)
        self.max_length = int(get_config_or_default(params, "max_length", "1000"))
        print(f"[DigestPlugin#{self.id}] initialized")

    def process(self, source_id: str | None, items: list[Item]) -> list[Item]:
        print(f"[DigestPlugin#{self.id}] process called, n={len(items)}")
        if source_id is None:
            raise Exception(f"[DigestPlugin#{self.id}] can not be scheduled")

        plugin_state_q = Query().plugin_id == self.id
        _d: Any = database_manager.plugin_states.get(plugin_state_q)  # type: ignore
        data: dict[str, Any] = (
            _d if _d is not None else {"plugin_id": self.id, "state": {}}
        )
        state = data["state"]

        items_as_dicts = list(map(item_to_dict, items))
        state[source_id] = items_as_dicts

        database_manager.plugin_states.upsert(  # type: ignore
            {"plugin_id": self.id, "state": state}, plugin_state_q
        )

        aggregated_items: list[Item] = []
        for data_source_id in state:
            source_item_dicts = state[data_source_id]
            source_items = map(dict_to_item, source_item_dicts)
            aggregated_items += source_items

        spans: list[Span] = group_by_time_span(
            aggregated_items, self.interval_pair, self.from_datetime
        )

        digest_items: list[Item] = []
        for span in spans:
            if len(span.items) == 0:
                continue

            digest_title = (
                f"{self.digest_title_prefix} {span.span_title}"
                if self.digest_title_prefix
                else span.span_title
            )
            digest_desc = (
                f"{self.digest_description}<br><br>" if self.digest_description else ""
            )
            for span_item in span.items:
                pub_date_stamp = (
                    span_item.pub_date.strftime("%a, %d %b %Y %H:%M:%S +0000")
                    if span_item.pub_date
                    else ""
                )
                author = span_item.author if span_item.author else ""
                digest_desc += f'<strong><a href="{span_item.link}">{span_item.title}</a></strong><br>'
                digest_desc += (
                    f"<small>{pub_date_stamp} <i>{author}</i></small><br><br>"
                )
                digest_desc += span_item.description if span_item.description else ""
                if len(digest_desc) > self.max_length:
                    digest_desc = f"{digest_desc[0:self.max_length]}..."

                digest_desc += "<br><br>"

            datetime_1970: datetime = datetime.fromtimestamp(0)
            digest_pub_date = (
                span.items[-1].pub_date if span.items[-1].pub_date else datetime_1970
            )
            digest_item: Item = Item(
                title=digest_title,
                description=digest_desc,
                link=self.digest_link,
                author=None,
                pub_date=digest_pub_date,
                category=None,
                comments=None,
                enclosures=[],
                guid=ItemGUID(f"aggro__{self.id}__{digest_pub_date.isoformat()}"),
                media_content=None,
            )

            digest_items.append(digest_item)

        print(
            f"[DigestPlugin#{self.id}] process returning items, n={len(digest_items)}"
        )

        return digest_items
