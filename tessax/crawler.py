import requests
from bs4 import BeautifulSoup, NavigableString, Comment
from urllib.parse import urljoin
from pydantic import BaseModel,  Field, model_validator
import re
import urllib3
import copy

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def req_html(url,timeout = 60) -> BeautifulSoup:
        try:
            req = requests.get(url,timeout=timeout, verify=False, headers=headers)
            req.raise_for_status()
            return BeautifulSoup(req.text,'html.parser')
        except Exception as e:
            print(e)
            return None
def format(soup:BeautifulSoup) -> BeautifulSoup:
    
        # test_tag= soup.find(id="hamburger-toolbar-page")
        
        if soup.title:     
            title_tag = copy.copy(soup.title)      
            soup.insert(1,title_tag)
            
        soup.head.decompose() 
        
        for tag in soup(["header","script"]):
            tag.decompose()   
                
        
        for element in soup(text=lambda text: isinstance(text, Comment)):
            element.decompose()        
        
        # for tag in (soup.find_all(True)):
        #     wrapped = any(isinstance(c, NavigableString) and c.strip() for c in tag.contents) and len(tag.contents)<2
        #     if tag.contents:
        #         empty =  not any(c.strip() for c in tag.contents if isinstance(tag.contents,NavigableString))
        #         if not empty:
        #             if wrapped:
        #                 tag.unwrap()
        #         else:
        #             tag.decompose()
                    
            
        tags  : list = ["video","img","link"]
        exclude_patterns : list = ["mailto:","tel:",".mp4"]   
        for tag in soup(tags):
                tag.decompose()
        return soup
    
def get_links(url,soup:BeautifulSoup) -> set:
        
        links : set = set()
        for link in soup("a",href=re.compile(r"^https?://|/")):                  
            path  = urljoin(str(url), str(link['href']))           
            links.add(path)           
        return links
    
class Crawler(BaseModel):
    
    """
        Crawler for webpages.
        
    """
    
    sources:set
    visited:set = Field(default_factory=set)
    depth: int = 5
    #chunker:Chunker 
    
    @model_validator(mode='after')
    def initialize_visited(self) -> 'Crawler':
        
        self.visited.update(self.sources)
        return self
    
    def __call__(self):
        
        for url in self.sources:
            generator = self.recursive_handler(url)
            for html in generator:
                #chunk function
                with open('out.html', 'w',encoding="utf-8") as f:
                    f.writelines(html.prettify()) 
                #pass
        
    #generator
    def recursive_handler(self,url,count = 0):
        
        
        self.visited.add(url)
        
        if count > self.depth:
            return
        
        html = req_html(url)
        links = get_links(url,html)
        
        formatted_html = format(html)
        yield formatted_html
       
        
        
        for link in links :
            if link not in self.visited:
                yield from self.recursive_handler(link,count=count+1)    
