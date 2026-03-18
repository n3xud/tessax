from abc import ABC, abstractmethod
from pydantic import BaseModel
from bs4 import BeautifulSoup


class HTMLSplitter(ABC, BaseModel):
    @abstractmethod
    def split(data: BeautifulSoup):
        """splits incoming html data

        Args:
            data (BeautifulSoup): html to split
        """
        pass
