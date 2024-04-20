from bs4 import BeautifulSoup
import time
from traceback import print_exc
import hashlib
from datetime import datetime, timezone
from typing import Any, TypeVar, cast, overload
import re
import requests
from app.Item import Item, ItemEnclosure, ItemGUID, ItemMediaContent
from app.PluginInterface import Params, PluginInterface
from app.utils import ItemDict, dump_to_file, get_config, get_config_or_default


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

    def absolute_link(self, link: str | list[str]) -> str:
        if type(link) == list:
            link = link[0]

        link = cast(str, link)
        if link.startswith("/") or link.startswith("#"):
            link = self.url + link

        return link

    def get_url(self, session: requests.Session, url: str):
        try:
            resp = session.get(url, allow_redirects=True)
            if resp.status_code >= 400:
                ex = Exception(f"status_code >= 400, got {resp.status_code}")
                ex.add_note(resp.text[0:1000])
                raise ex
        except Exception as ex:
            ex.add_note(f"{self.log_prefix} failed to fetch page, url: {url}")
            raise

        return resp

    def parse_html(self, from_url: str, html: str):
        try:
            elem = BeautifulSoup(html, "html.parser")
        except Exception as ex:
            dump_file_name = dump_to_file(self.id, html)
            ex.add_note(
                f"{self.log_prefix} failed to parse HTML from {from_url}, HTML dumped to {dump_file_name}"
            )
            raise

        return elem

    def eval_selector(
        self, selector: str | None, ctx: dict[str, Any]
    ) -> list[BeautifulSoup]:
        if not selector:
            return []

        try:
            elems = eval(selector, ctx)
        except Exception as ex:
            dump_file_name = dump_to_file(self.id, str(ctx))
            ex.add_note(
                f"{self.log_prefix} failed to eval selector:\n  {selector}\n"
                + f"HTML dumped to {dump_file_name}.\n"
            )
            raise

        return elems

    def process(self, source_id: str | None, items: list[Item]) -> list[Item]:
        if source_id is not None:
            raise Exception(
                f"{self.log_prefix} can only be scheduled, trying to propagate items from source {source_id}"
            )

        self.log(f'starting to scrape posts from URL "{self.url}"')

        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/114.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Pragma": "no-cache",
            "Cache-Control": "no-cache",
            "TE": "trailers",
        }

        result_items: list[Item] = []
        with requests.session() as session:
            session.headers.update(headers)

            # Fetch the page
            page_resp = self.get_url(session, url=self.url)

            # Parse the page
            page_elem = self.parse_html(from_url=self.url, html=page_resp.text)

            # Evaluate post selector on parsed page
            ctx: dict[str, BeautifulSoup | None] = {"page": page_elem}
            post_elems = self.eval_selector(self.selector_post, ctx=ctx)

            if post_elems is None:
                post_elems = []

            # For each post on page
            for post_elem in post_elems:
                ctx_with_post: dict[str, BeautifulSoup | None] = {
                    "page": page_elem,
                    "post": post_elem,
                }

                # Evaluate link selector on post
                link_elems = self.eval_selector(self.selector_link, ctx=ctx_with_post)
                detail_page_url = (
                    self.absolute_link(link_elems[0]["href"])
                    if len(link_elems) > 0
                    else None
                )

                # Fetch and parse post detail page
                if detail_page_url:
                    # Fetch
                    self.log(f"scraping detail page: {detail_page_url}")
                    detail_page_resp = self.get_url(session, url=detail_page_url)
                    detail_page_elem = self.parse_html(
                        from_url=detail_page_url, html=detail_page_resp.text
                    )

                    guid = ItemGUID(detail_page_url, is_perma_link=True)
                else:
                    detail_page_elem = None
                    guid = None

                ctx_with_post_detail: dict[str, BeautifulSoup | None] = {
                    "page": page_elem,
                    "post": post_elem,
                    "detail_page": detail_page_elem,
                }

                # Evaluate title selector on post
                title_elems = self.eval_selector(
                    self.selector_title, ctx=ctx_with_post_detail
                )
                title = (
                    title_elems[0].get_text().strip() if len(title_elems) > 0 else None
                )

                # Evaluate description selector on post
                description_elems = self.eval_selector(
                    self.selector_description, ctx=ctx_with_post_detail
                )
                description = (
                    str(description_elems[0]).strip()
                    if len(description_elems) > 0
                    else None
                )

                # Evaluate date selector on post
                date_elems = self.eval_selector(
                    self.selector_date, ctx=ctx_with_post_detail
                )
                date = date_elems[0].get_text().strip() if len(date_elems) > 0 else None

                # Evaluate author selector on post
                author_elems = self.eval_selector(
                    self.selector_author, ctx=ctx_with_post_detail
                )
                author = (
                    author_elems[0].get_text().strip()
                    if len(author_elems) > 0
                    else None
                )

                try:
                    image_elems = self.eval_selector(
                        self.selector_image, ctx=ctx_with_post_detail
                    )
                    image_elem = image_elems[0] if len(image_elems) > 0 else None
                    image_src: str | None = None
                except Exception:
                    print_exc()
                    self.log(
                        f"failed to extract image source with selector: {self.selector_image}, skipping image"
                    )
                    image_src = None

                if image_elem:
                    if image_elem.has_attr("src"):
                        image_src = cast(str, image_elem["src"])
                    elif image_elem.has_attr("content"):
                        image_src = cast(str, image_elem["content"])
                    elif image_elem.has_attr("href"):
                        image_src = cast(str, image_elem["href"])
                    elif (
                        image_elem.has_attr("style")
                        and "background-image:" in image_elem["style"]
                    ):
                        match = re.match(
                            r"background-image:\s*url\((?P<url>.*?)\)",
                            cast(str, image_elem["style"]),
                        )
                        if match is None:
                            raise Exception(
                                f"{self.log_prefix} weird regex result when looking for background-image"
                            )
                        image_src = cast(str, match.group("url").strip("'\""))

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

                if image_src:
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
