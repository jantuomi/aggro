from bs4 import BeautifulSoup
import time
import hashlib
from datetime import datetime, timezone
from typing import Any
import re
import requests
from app.Item import Item, ItemEnclosure, ItemGUID, ItemMediaContent
from app.PluginInterface import Params, PluginInterface
from app.utils import ItemDict, get_config, get_config_or_default


class Plugin(PluginInterface):
    def __init__(self, id: str, params: Params) -> None:
        super().__init__("ScraperSourcePlugin", id, params)
        self.url: str = get_config(params, "url").strip("/")
        self.selector_post: str = get_config(params, "selector_post")
        self.selector_title: str | None = get_config_or_default(
            params, "selector_title", None
        )
        self.selector_date: str | None = get_config_or_default(
            params, "selector_date", None
        )
        self.selector_link: str | None = get_config_or_default(
            params, "selector_link", None
        )
        self.selector_description: str | None = get_config_or_default(
            params, "selector_description", None
        )
        self.selector_author: str | None = get_config_or_default(
            params, "selector_author", None
        )
        self.selector_image: str | None = get_config_or_default(
            params, "selector_image", None
        )
        self.show_image_in_description: bool = get_config_or_default(
            params, "show_image_in_description", True
        )

        print(f"[ScraperSourcePlugin#{self.id}] initialized")

    def absolute_link(self, link: str) -> str:
        if link.startswith("/") or link.startswith("#"):
            link = self.url + link

        return link

    def process(self, source_id: str | None, items: list[Item]) -> list[Item]:
        if source_id is not None:
            raise Exception(
                f"{self.log_prefix} can only be scheduled, trying to propagate items from source {source_id}"
            )

        self.log(f'starting to scrape posts from URL "{self.url}"')

        result_items: list[Item] = []
        with requests.session() as session:
            page_resp = session.get(self.url, allow_redirects=True)
            page_elem = BeautifulSoup(page_resp.text, "html.parser")
            post_elems = eval(self.selector_post, {"page": page_elem})

            for post_elem in post_elems:
                if self.selector_link:
                    link_elem = eval(
                        self.selector_link, {"page": page_elem, "post": post_elem}
                    )[0]
                    detail_page_url = self.absolute_link(link_elem["href"])

                else:
                    detail_page_url = None

                if detail_page_url:
                    detail_page_resp = session.get(
                        detail_page_url, allow_redirects=True
                    )
                    detail_page_elem = BeautifulSoup(
                        detail_page_resp.text, "html.parser"
                    )
                    guid = ItemGUID(detail_page_url, is_perma_link=True)
                else:
                    detail_page_elem = None
                    guid = None

                if self.selector_title:
                    title_elem = eval(
                        self.selector_title,
                        {
                            "page": page_elem,
                            "post": post_elem,
                            "detail_page": detail_page_elem,
                        },
                    )[0]
                    title = title_elem.get_text().strip()
                else:
                    title = None

                if self.selector_description:
                    description_elem = eval(
                        self.selector_description,
                        {
                            "page": page_elem,
                            "post": post_elem,
                            "detail_page": detail_page_elem,
                        },
                    )[0]
                    description = str(description_elem).strip()
                else:
                    description = None

                if self.selector_date:
                    date_elem = eval(
                        self.selector_date,
                        {
                            "page": page_elem,
                            "post": post_elem,
                            "detail_page": detail_page_elem,
                        },
                    )[0]
                    date = date_elem.get_text().strip()
                else:
                    date = None

                if self.selector_author:
                    author_elem = eval(
                        self.selector_author,
                        {
                            "page": page_elem,
                            "post": post_elem,
                            "detail_page": detail_page_elem,
                        },
                    )[0]
                    author = author_elem.get_text().strip()
                else:
                    author = None

                if self.selector_image:
                    image_elem = eval(
                        self.selector_image,
                        {
                            "page": page_elem,
                            "post": post_elem,
                            "detail_page": detail_page_elem,
                        },
                    )[0]
                    if image_elem.has_attr("src"):
                        image_src = image_elem["src"]
                    elif image_elem.has_attr("href"):
                        image_src = image_elem["href"]
                    elif (
                        image_elem.has_attr("style")
                        and "background-image:" in image_elem["style"]
                    ):
                        match = re.match(
                            r"background-image:\s*url\((?P<url>.*?)\)",
                            image_elem["style"],
                        )
                        if match is None:
                            raise Exception(
                                f"{self.log_prefix} weird regex result when looking for background-image"
                            )
                        image_src = match.group("url").strip("'\"")
                    else:
                        image_src = None
                else:
                    image_src = None

                if guid is None:
                    if title:
                        guid = ItemGUID(f"aggro__{self.id}__{title}")
                    elif description:
                        digest = str(hashlib.sha256(description.encode("utf-8")))
                        guid = ItemGUID(f"aggro__{self.id}__{digest[:32]}")
                    else:
                        raise Exception(
                            f"{self.log_prefix} both title and description are None"
                        )

                if image_src is not None:
                    image_src = self.absolute_link(image_src)
                    image_html = f'<img src="{image_src}"><br><br>'
                    if description and self.show_image_in_description:
                        description = image_html + description
                    elif description is None:
                        description = image_html

                    media_content = ItemMediaContent(
                        url=image_src,
                        medium="image",
                    )
                else:
                    media_content = None

                if description:
                    description = description.replace('src="/', f'src="{self.url}/')
                    description = description.replace('src="#', f'src="{self.url}#')
                    description = description.replace('href="/', f'href="{self.url}/')
                    description = description.replace('href="#', f'href="{self.url}#')

                item = Item(
                    title=f"{date} – {title}",
                    link=detail_page_url if detail_page_url else self.url,
                    description=description,
                    pub_date=None,  # TODO pub_date parsing
                    author=author,
                    category=None,
                    comments=None,
                    enclosures=[],
                    guid=guid,
                    media_content=media_content,
                )
                result_items.append(item)

        self.log(f'scraped {len(result_items)} posts from URL "{self.url}"')
        return result_items
