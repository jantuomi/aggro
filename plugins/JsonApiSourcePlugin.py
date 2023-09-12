import json
from typing import Any
import hashlib
import requests
from app.Item import Item, ItemGUID, ItemMediaContent
from app.PluginInterface import Params, PluginInterface
from app.utils import ItemDict, get_config, get_config_or_default


class Plugin(PluginInterface):
    def __init__(self, id: str, params: Params) -> None:
        super().__init__("JsonApiSourcePlugin", id, params)
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

        self.log("initialized")

    def absolute_link(self, link: str) -> str:
        if link.startswith("/") or link.startswith("#"):
            link = self.url + link

        return link

    def process(self, source_id: str | None, items: list[Item]) -> list[Item]:
        if source_id is not None:
            raise Exception(
                f"{self.log_prefix} can only be scheduled, trying to propagate items from source {source_id}"
            )

        self.log(f'fetching data from JSON API at URL "{self.url}"')

        result_items: list[Item] = []
        with requests.session() as session:
            api_resp = session.get(self.url, allow_redirects=True)
            data = json.loads(api_resp.text)
            post_items = eval(self.selector_post, {"data": data})

            for post in post_items:
                if self.selector_link:
                    link = eval(
                        self.selector_link, {"post": post, "data": data}
                    ).strip()
                    guid = ItemGUID(link, is_perma_link=True)
                else:
                    link = None
                    guid = None

                if self.selector_title:
                    title = eval(
                        self.selector_title, {"post": post, "data": data}
                    ).strip()
                else:
                    title = None

                if self.selector_description:
                    description = eval(
                        self.selector_description, {"post": post, "data": data}
                    ).strip()
                else:
                    description = None

                if self.selector_date:
                    date = eval(
                        self.selector_date, {"post": post, "data": data}
                    ).strip()
                else:
                    date = None

                if self.selector_author:
                    author = eval(
                        self.selector_author, {"post": post, "data": data}
                    ).strip()
                else:
                    author = None

                if self.selector_image:
                    image_src = eval(
                        self.selector_image, {"post": post, "data": data}
                    ).strip()
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
                    link=link if link else self.url,
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

        self.log(f"fetched {len(result_items)} items from JSON API")
        return result_items
