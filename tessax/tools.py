import nltk
from nltk.tokenize import sent_tokenize
import typing as t
from transformers import AutoModel

from . import database
from .embedding import create_retrieval_embedding
from .config import cfg
nltk.download('punkt_tab')

def tokenize(text : str)-> t.List[str]:

    sentences = sent_tokenize(text)
 
    return sentences
    
def retrieve_context(text) -> t.List[str]:
    
    embedding = create_retrieval_embedding(text)
    
    nodes = database.search(text,embedding)
    
    context = [node[1] for node in nodes]
    
    
    #add parents context
    if cfg.add_parent_context:
        parent_context = add_parent_context(nodes)
        context.extend(parent_context)
        
    #add sibling context   
    if cfg.add_sibling_context:
        sibling_context = add_sibling_context(nodes,text)
        context.extend(sibling_context)
        
       
    return(context)


def add_parent_context(nodes):
    parent_context = []
    parents = [node[0] for node in nodes]
    
    for parent in set(parents):
        
        row = database.get_parent(parent)
        if row[1]:
            parent_context.append(row[1])
    print(parent_context)
    return parent_context
    
    
def add_sibling_context(nodes):
    sibling_context = []
    parents_id = [node[2] for node in nodes]
    
    for parent_id in set(parents_id):
        rows = database.get_siblings(parent_id)
        for row in rows:
            if row[1]:
                sibling_context.append(row[1])
    
    
    print(sibling_context)
    return sibling_context





