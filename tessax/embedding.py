import os
os.environ["HF_HUB_OFFLINE"] = "0"
from sentence_transformers import SentenceTransformer



import torch
from bs4 import Tag
_embedding_model_text_matching = SentenceTransformer(
    "jinaai/jina-embeddings-v5-text-small-text-matching",
    model_kwargs={"dtype": torch.bfloat16},
    trust_remote_code=True
)
_embedding_model_retrieval = SentenceTransformer(
    "jinaai/jina-embeddings-v5-text-small-retrieval",
    model_kwargs={"dtype": torch.bfloat16},
    trust_remote_code=True
)
tokenizer = _embedding_model_text_matching.tokenizer
    
def tokenizer_encode(text):
    
    encoded = tokenizer.encode(text, add_special_tokens=False)
    return encoded


    
def get_token_length(data : str | list | Tag ):
    
    if isinstance(data,list):
       
        tag_str_list = ["".join(tag.find_all(string=True, recursive=False)).strip() for tag in data]
        tag_str_list= "".join(tag_str_list)
        data = tag_str_list
    
    elif isinstance(data,Tag):
        
        strings = data.find_all(string=True, recursive=False)
        data = " ".join(strings).strip()
    output = tokenizer_encode(data)
    token_count = len(output)    
    return token_count





def create_doc_embedding(query):
    
    document_embeddings = _embedding_model_retrieval.encode(sentences=query, prompt_name="document")
    return document_embeddings

def create_retrieval_embedding(query):
    
    document_embeddings = _embedding_model_retrieval.encode(sentences=query, prompt_name="query")
    return document_embeddings


def _get_similarities(e1,e2):
    emb1 = _embedding_model_text_matching.encode(e1)
    emb2 = _embedding_model_text_matching.encode(e2)
    similarities = _embedding_model_text_matching.similarity(emb1,emb2)
    return similarities