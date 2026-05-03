"""This module contains tools for scraping web pages and formatting html"""


import requests
from bs4 import BeautifulSoup, NavigableString, Comment, Tag
from urllib.parse import urljoin
from pydantic import BaseModel, Field, model_validator, HttpUrl
import re
import urllib3
import copy
from .config import RAGConfig
from .node import Node
from . import tools

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}


def req_html(url:str, timeout=60) -> BeautifulSoup:
    """Sends a requests to a webpage and retrieves the HTML.

    Args:
        url (str): URL 
        timeout (int, optional): Time before requests timeouts. Defaults to 60.

    Returns:
        BeautifulSoup: _description_
    """
    try:
        req = requests.get(url, timeout=timeout, verify=False, headers=headers)
        req.raise_for_status()
        return BeautifulSoup(req.text, "html.parser",multi_valued_attributes=None)
    except requests.exceptions.RequestException as re:
        print(f"skipping {url} due to error {re}")
        return None


def format(soup: BeautifulSoup) -> BeautifulSoup:
    """Formats HTML for further analysis.

    Args:
        soup (BeautifulSoup): unformatted HTML

    Returns:
        BeautifulSoup: formatted HTML
    """


    #Extracts title and puts it in the first position
    if soup.title:
        title_tag = copy.copy(soup.title)
        soup.insert(1, title_tag)


    #Removes head section
    if soup.head:
        soup.head.decompose()

    #Removes any js, css, links, videos and images
    tags_to_remove = ["script", "style","video", "img", "link"]
    for tag in soup(tags_to_remove):
        tag.decompose()

    #Removes comments
    for element in soup(text=lambda text: isinstance(text, Comment)):
        element.decompose()

    for tag in reversed(soup.find_all(True)):
        
        #Removes tags with class hidden
        if re.search(r"hidden",tag.get("class",""),re.IGNORECASE):
            tag.decompose()
            
        #Removes empty tags    
        is_empty = all(
            isinstance(c, NavigableString) and not c.strip() for c in tag.contents
        )
        if is_empty :
            tag.decompose()
            continue

        #Unwrap a and strong tags
        if tag.name in ["a","strong"]:
            tag.unwrap()

        #Unwraps tags with only one child and no direct text
        child_tags = [c for c in tag.contents if isinstance(c, Tag)]
        child_strings = [c for c in tag.contents if isinstance(c, NavigableString)]

        has_only_one_tag = len(child_tags) == 1
        has_no_direct_text = all(not s.strip() for s in child_strings)

        if has_only_one_tag and has_no_direct_text:
            tag.unwrap()
            continue

    return soup


def get_links(url:str, soup: BeautifulSoup) -> set:
    """Retrieves links from webpage

    Args:
        url (str): URL
        soup (BeautifulSoup): HTML of URL

    Returns:
        set: Set of links
    """

    links: set = set()
    for link in soup("a", href=re.compile(r"^https?://|/")):
        path = urljoin(url, str(link["href"]))
        links.add(path)
    return links



class HTMLReader(BaseModel):
    """Crawls a set of source URLs and yields parsed page data as nested node trees.

    Recursively follows links found on each page, avoiding duplicates via a
    visited set. Each page is parsed into a nested Node tree representing
    the HTML tag structure.

    Attributes:
        sources (set): Seed URLs to begin crawling from.
        config (Config): Settings that control crawling behaviour (e.g. title extraction).
        visited (set): URLs already crawled, pre-populated with sources on init.
        title (str): Title of the most recently crawled page, or None if unavailable.

    Example:
        reader = HTMLReader(sources={"https://example.com"}, config=config)
        for root_node, html in reader:
            print(root_node,html)
    """
   

    pages: set[HttpUrl]
    config : RAGConfig
    visited: set = Field(
        default_factory=set,
        description="stores already visited sites to prevent duplicates",
    )
    title : str = None
    
    @model_validator(mode="after")
    def initialize_visited(self) -> "HTMLReader":

        self.visited.update(self.pages)
        return self

    def __iter__(self):
        for url in self.pages:
            yield from self._crawl(str(url))
                
    def _crawl(self, url:str):
        """Recursively crawl a URL and all links found on its page.
    
        Yields:
            root_node (Node): Root of the nested tree representing the page's HTML structure.
            formatted_html (BeautifulSoup): The formatted HTML of the crawled page.
        """
        #Add url to set of visited
        self.visited.add(url)
        #Request HTML
        html = req_html(url)

        if html is None:
            return
        #Get every link on webpage
        links = get_links(url, html)
        #Get title of webpage
        #Doing it here so it does not get executed multiple times in recursive create_nodes function
        #Subject to change
        if html.title and self.config.title:
            self.title = html.title.get_text()
        else:
            self.title = None
        #Format HTML    
        formatted_html = format(html)
        #Create nested tree
        root_node = self.create_nodes(formatted_html)
        yield root_node, formatted_html

        #Crawl the found links with a recursive function call
        if self.config.recursive:
            for link in links:
                if link not in self.visited:
                    yield from self._crawl(link)
                
    def create_nodes(self,soup:BeautifulSoup,parent=None)-> Node:
        """Creates a nested tree out of HTML tags.

        Args:
            soup (BeautifulSoup): HTML
            parent (_type_, optional): Parent for node. Defaults to None.

        Returns:
            Node: Root node of nested tree.
        """
        
        content = soup.find_all(string=True, recursive=False)
        content_str = "".join(content).strip() or None
        sentences = None
        #Extract sentences out of string
        if content_str:
            sentences = tools.tokenize(content_str)
    
    
        root_node = Node(content=sentences,tag=[soup.name],title=self.title)
        if parent:
                root_node.parent=parent

        for child_tag in soup.find_all(recursive=False):

            if isinstance(child_tag,Tag):
                child_node = self.create_nodes(child_tag,root_node)
                root_node.add_children(child_node)
                
        return root_node