import random
import time
import requests
import re
import urllib.parse
from datetime import datetime, timedelta
from bs4 import BeautifulSoup, Tag
from app.Item import Item
from app.PluginInterface import Params, PluginInterface
from app.utils import get_config, get_config_or_default


def replace_lm_links(text: str) -> str:
    # Use regular expression to find all occurrences of the link pattern
    pattern = r"https://lm\.facebook\.com/l\.php\?u=([a-zA-Z0-9%._-]+)"
    matches = re.findall(pattern, text)

    # Iterate through all matches and replace them with the decoded URL
    for match in matches:
        decoded_url = urllib.parse.unquote(match)
        text = text.replace(f"https://lm.facebook.com/l.php?u={match}", decoded_url)

    return text


def parse_custom_date(date_str: str) -> datetime:
    current_year = datetime.now().year  # Get the current year if not provided

    try:
        # Try parsing assuming the year is provided
        return datetime.strptime(date_str, "%B %d, %Y at %I:%M %p")
    except ValueError:
        pass

    try:
        # Try parsing assuming the current year
        return datetime.strptime(f"{date_str} {current_year}", "%B %d at %I:%M %p %Y")
    except ValueError:
        pass

    # Parse relative times like "14 hrs" and "20 mins"
    now = datetime.now()
    match = re.match(r"(\d+)\s*(hr|hrs|min|mins)\s*", date_str, re.IGNORECASE)
    if match:
        amount, unit = match.groups()
        amount = int(amount)
        if unit.lower().startswith("hr"):
            delta = timedelta(hours=amount)
        elif unit.lower().startswith("min"):
            delta = timedelta(minutes=amount)
        else:
            raise ValueError("Unparseable date: " + date_str)

        return now - delta

    raise ValueError("Unparseable date: " + date_str)


def fetch_page_posts(email: str, password: str, page_id: str, limit: int) -> list[Item]:
    base_url = "https://mbasic.facebook.com"
    with requests.session() as session:
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/114.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "DNT": "1",
            "Alt-Used": "mbasic.facebook.com",
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
        session.headers.update(headers)

        cookie_page_resp = session.get(
            f"{base_url}/login/", headers=headers, allow_redirects=True
        )
        if cookie_page_resp.status_code >= 400:
            raise Exception(cookie_page_resp.text)

        cookie_page = BeautifulSoup(cookie_page_resp.text, features="xml")
        lsd: str = cookie_page.find("input", {"name": "lsd"})["value"]  # type: ignore
        jazoest: str = cookie_page.find("input", {"name": "jazoest"})["value"]  # type: ignore

        cookie_post_url = f"{base_url}/cookie/consent/?next_uri=https%3A%2F%2Fmbasic.facebook.com%2Flogin"

        time.sleep(random.randrange(1000, 3000) / 1000.0)

        login_page_resp = session.post(
            cookie_post_url,
            data={
                "lsd": lsd,
                "jazoest": jazoest,
                "accept_only_essential": "1",
            },
            verify=False,
            allow_redirects=True,
            headers=headers,
        )

        if login_page_resp.status_code >= 400:
            raise Exception(login_page_resp.text)

        login_page = BeautifulSoup(login_page_resp.text, features="lxml")

        lsd: str = login_page.find("input", {"name": "lsd"})["value"]  # type: ignore
        jazoest: str = login_page.find("input", {"name": "jazoest"})["value"]  # type: ignore
        mts: str = login_page.find("input", {"name": "m_ts"})["value"]  # type: ignore
        li: str = login_page.find("input", {"name": "li"})["value"]  # type: ignore
        try_number: str = login_page.find("input", {"name": "try_number"})["value"]  # type: ignore
        unrecognized_tries: str = login_page.find(  # type: ignore
            "input", {"name": "unrecognized_tries"}
        )["value"]

        login_post_url = (
            f"{base_url}/login/device-based/regular/login/?refsrc=deprecated&lwv=100"
        )

        time.sleep(random.randrange(1000, 3000) / 1000.0)

        login_post_resp = session.post(
            login_post_url,
            data={
                "lsd": lsd,
                "jazoest": jazoest,
                "m_ts": mts,
                "li": li,
                "try_number": try_number,
                "unrecognized_tries": unrecognized_tries,
                "email": email,
                "pass": password,
                "login": "Log+in",
                "bi_xrwh": "0",
            },
            headers=headers,
            verify=False,
            allow_redirects=True,
        )

        if login_post_resp.status_code >= 400:
            raise Exception(login_post_resp.text)

        page_timeline_url = f"{base_url}/{page_id}?v=timeline"
        items: list[Item] = []
        done = False
        while len(items) < limit and not done:
            time.sleep(random.randrange(1000, 3000) / 1000.0)

            timeline_resp = session.get(
                page_timeline_url, headers=headers, allow_redirects=True
            )

            if timeline_resp.status_code >= 400:
                raise Exception(timeline_resp.text)

            timeline = BeautifulSoup(timeline_resp.text, features="lxml")
            posts = timeline.select("section > article")

            for post in posts:
                link_tag: Tag | None = post.find("a", string="Full Story")  # type: ignore
                time_tag: Tag = post.find("abbr")  # type: ignore
                link = f"{base_url}{link_tag['href']}" if link_tag is not None else None
                pub_date_str: str = time_tag.get_text()
                pub_date = parse_custom_date(pub_date_str)
                story_body_container = str(post.find("div"))
                story_body_container.replace('href="/', f'href="{base_url}/')
                story_body_container = replace_lm_links(story_body_container)
                title = f"{page_id} on {pub_date.strftime('%d.%m.%Y at %H:%M')}"
                item = Item(
                    title=title,
                    description=story_body_container,
                    link=link,
                    guid=link if link is not None else f"aggro__facebook__{title}",
                    author=page_id,
                    category=None,
                    comments=None,
                    enclosures=[],
                    pub_date=pub_date,
                )
                items.append(item)

                if len(items) == limit:
                    break

            see_more_stories_tag = timeline.find("a", string="See more stories")
            if see_more_stories_tag is None:
                done = True
                break

            page_timeline_url: str = see_more_stories_tag["href"]  # type: ignore
            page_timeline_url = f"{base_url}{page_timeline_url}"

        return items


class Plugin(PluginInterface):
    def __init__(self, id: str, params: Params) -> None:
        super().__init__(id, params)
        self.login_email = get_config(params, "login_email")
        self.login_password = get_config(params, "login_password")
        self.page_id = get_config(params, "page_id")
        self.limit = int(get_config_or_default(params, "limit", "10"))

        print(f"[FacebookSourcePlugin#{self.id}] initialized")

    def process(self, source_id: str | None, items: list[Item]) -> list[Item]:
        print(f"[FacebookSourcePlugin#{self.id}] process called")
        if source_id is not None:
            raise Exception(
                f"FacebookSourcePlugin#{self.id} can only be scheduled, trying to process items from source {source_id}"
            )

        posts = fetch_page_posts(
            self.login_email, self.login_password, self.page_id, self.limit
        )

        print(f"[FacebookSourcePlugin#{self.id}] process returns items, n={len(posts)}")
        return posts
