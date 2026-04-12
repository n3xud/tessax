from abc import ABC, abstractmethod
from pydantic import BaseModel
from bs4 import BeautifulSoup

from tessax.node import Node


class HTMLSplitter(BaseModel,ABC):
    
   
    
    @abstractmethod
    def merge(node:Node):
        pass

    @abstractmethod
    def vectorize():
        pass
    