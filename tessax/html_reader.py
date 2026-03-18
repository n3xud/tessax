import requests
from bs4 import BeautifulSoup, NavigableString, Comment, Tag
from urllib.parse import urljoin
from pydantic import BaseModel, Field, model_validator
import re
import urllib3
import copy

from .splitter.html_splitter import HTMLSplitter

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}


def req_html(url, timeout=60) -> BeautifulSoup:
    try:
        req = requests.get(url, timeout=timeout, verify=False, headers=headers)
        req.raise_for_status()
        return BeautifulSoup(req.text, "html.parser")
    except requests.exceptions.RequestException as re:
        print(f"skipping {url} due to error {re}")
        return None


def format(soup: BeautifulSoup) -> BeautifulSoup:

    if soup.title:
        title_tag = copy.copy(soup.title)
        soup.insert(1, title_tag)

    soup.head.decompose()

    for tag in soup(["header", "script", "style"]):
        tag.decompose()

    for element in soup(text=lambda text: isinstance(text, Comment)):
        element.decompose()

    for tag in reversed(soup.find_all(True)):
        is_empty = all(
            isinstance(c, NavigableString) and not c.strip() for c in tag.contents
        )

        void_elements = ["br", "hr"]

        if is_empty and tag.name not in void_elements:
            tag.decompose()
            continue

        child_tags = [c for c in tag.contents if isinstance(c, Tag)]
        child_strings = [c for c in tag.contents if isinstance(c, NavigableString)]

        has_only_one_tag = len(child_tags) == 1
        has_no_direct_text = all(not s.strip() for s in child_strings)

        if has_only_one_tag and has_no_direct_text:
            tag.unwrap()

    tags: list = ["video", "img", "link"]
    # exclude_patterns : list = ["mailto:","tel:",".mp4"]
    for tag in soup(tags):
        tag.decompose()
    return soup


def get_links(url, soup: BeautifulSoup) -> set:

    links: set = set()
    for link in soup("a", href=re.compile(r"^https?://|/")):
        path = urljoin(str(url), str(link["href"]))
        links.add(path)
    return links


class HTMLReader(BaseModel):
    """
    Crawler for webpages.

    """

    sources: set
    visited: set = Field(
        default_factory=set,
        description="stores already visited sites to prevent duplicates",
    )
    depth: int = Field(default=5, description="recursive depth")
    htmlsplitter: HTMLSplitter | None = None

    @model_validator(mode="after")
    def initialize_visited(self) -> "HTMLReader":

        self.visited.update(self.sources)
        return self

    def run(self):
        for url in self.sources:
            generator = self.recursive_handler(url)
            for html in generator:
                print(html)
                pass

    # generator
    def recursive_handler(self, url, count=0):

        self.visited.add(url)

        if count > self.depth:
            return

        html = req_html(url)
        print(html)
        if html is None:
            return

        links = get_links(url, html)

        formatted_html = format(html)
        yield formatted_html

        for link in links:
            if link not in self.visited:
                yield from self.recursive_handler(link, count=count + 1)
