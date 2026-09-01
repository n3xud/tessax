"""This module contains tools for scraping web pages and formatting html"""

from tessax.embedding import get_token_length,_get_similarities

import requests
from bs4 import BeautifulSoup, NavigableString, Comment, Tag
from urllib.parse import urljoin
from pydantic import BaseModel, Field, model_validator, HttpUrl
import re
import urllib3
import copy
from dataclasses import dataclass,field
from .config import cfg, ChunkModes
from .node import Node





urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)





headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
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
        print("request made")
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
        
        #Removes empty tags  
        is_empty = all(
            isinstance(c, NavigableString) and not c.strip() for c in tag.contents
        )
        if is_empty :
            tag.decompose()
            continue
        #Removes tags with class hidden
        if re.search(r"hidden",tag.get("class",""),re.IGNORECASE):
            tag.decompose()
            continue
        
        #Unwrap a and strong tags
        if tag.name in ["a","strong","ul"]:
            tag.unwrap()
            continue
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



@dataclass
class Cache():
    tags: list | None = field(default_factory=list)
    nodes : list | None = field(default_factory=list)
cache = Cache()
def create_nodes_super(soup:BeautifulSoup):
    
    def x(tag:Tag):
        
        tags = Cache([tag])
        found_tags = Cache()
        for ele in reversed(tag.find_all(recursive=False)):
            if isinstance(ele,Tag):       
                value = x(ele)
                found_tags = compare(value,found_tags)
        tags = compare(tags,found_tags)
        return tags
    tags = x(soup)

    root_node = create_node(tags)
    return root_node
    

def create_node(tags:Cache):
    tag_str_list = ["".join(tag.find_all(string=True, recursive=False)).strip() for tag in tags.tags]
    tag_str_list= "".join(tag_str_list)
    data = tag_str_list
    node = Node(content=[data])
    
    for child in tags.nodes:
        child.parent = node
        node.children.append(child)  
    
    return node 
    

def compare_size(elem:Cache,elem2:Cache):
    if get_token_length(elem.tags + elem2.tags) < cfg.chunk_size:
        return True
    return False
def compare_simil(elem:Cache,elem2:Cache):  
    e1 = "".join("".join(t.find_all(string=True, recursive=False)).strip() for t in elem.tags)
    e2 = "".join("".join(t.find_all(string=True, recursive=False)).strip() for t in elem2.tags)
    if not e1 or not e2:
        similarity = 1.0

    else:
        
        similarity = _get_similarities(e1,e2)
    if similarity> cfg.simil:
        
        return True
        
    else:
        return False
    
CHUNKERS  = {
    ChunkModes.FIXED_CHUNKING: compare_size ,
    ChunkModes.SEMANTIC_CHUNKING: compare_simil,
}

def compare(elem:Cache,elem2:Cache): 
    
    compare_fnc = CHUNKERS.get(cfg.chunk_mode)
    if compare_fnc(elem,elem2):
           
            return Cache(elem.tags + elem2.tags, elem.nodes + elem2.nodes)
    
    else: 
        if elem2.tags:
            node = create_node(elem2)  
            return Cache(elem.tags,[node] + elem.nodes)
        else:
            node = create_node(elem)
            return Cache([],[node] + elem.nodes)
     
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
   

    page: HttpUrl
    title : str = None
    
    

                
    def crawl(self,html = None):
        
        
        #Request HTML
        if html is None:
            
            html = req_html(self.page)

        if html is None:
            return
       
        if html.title and cfg.title:
            self.title = html.title.get_text()
        else:
            self.title = None
        #Format HTML    
        formatted_html = format(html)
        #Create nested tree
        root_node = self.create_nodes(formatted_html)
        return root_node, formatted_html

        
                
    def create_nodes(self,soup:BeautifulSoup,parent=None)-> Node:
        """Creates a nested tree out of HTML tags.

        Args:
            soup (BeautifulSoup): HTML
            parent (_type_, optional): Parent for node. Defaults to None.

        Returns:
            Node: Root node of nested tree.
        """
        
        
        root_node = create_nodes_super(soup=soup)    
        return root_node
    
    
    
            
            