import nltk
from nltk.tokenize import sent_tokenize
import typing as t
from transformers import AutoModel

from . import database
from .embedding import create_embedding
nltk.download('punkt_tab')

def tokenize(text : str)-> t.List[str]:

    sentences = sent_tokenize(text)
 
    return sentences
    
def retrieve_context(text) -> t.List[str]:
    
    embedding = create_embedding(text)
    
    nodes = database.search(text,embedding)
    
    context = [node[1] for node in nodes]
    
    
    #add parents context
    if True:
        parent_context = add_parent_context(nodes)
        context.append(parent_context)
        
    #add sibling context   
    if True:
        sibling_context = add_sibling_context(nodes)
        
        
        
    return(context)


def add_parent_context(nodes):
    parent_context = []
    parents = [node[0] for node in nodes]
    
    for parent in set(parents):
        
        row = database.get_parent(parent)
        if row[1]:
            parent_context.append(row[1])
            
    return parent_context
    
    
def add_sibling_context(nodes):
    sibling_context = []
    parents_id = [node[2] for node in nodes]
    
    for parent_id in set(parents_id):
        row = database.get_siblings(parent_id)
        if row[1]:
            sibling_context.append(row[1])
    
    return sibling_context


def logger(func):
    def inner():
        func()
        
    return inner


model = AutoModel.from_pretrained(
    'jinaai/jina-reranker-v3',
    dtype="auto",
    trust_remote_code=True,
)

def rerank(query,document):
    results = model.rerank(query,document)
    return results