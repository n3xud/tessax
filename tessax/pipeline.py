from index import Index
from html_reader import HTMLReader
from chunking.html_splitter import HTMLSplitter
from eval import Evaluation
from pydantic import BaseModel


class RAGPipeline(BaseModel):
    """
    Supported file formats:
        HTML
        ...
    """

    index: Index
    htmlreader: HTMLReader
    htmlsplitter: HTMLSplitter
    evaluation: Evaluation

    pass
