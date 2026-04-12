from sentence_transformers import SentenceTransformer
import torch

_embedding_model = SentenceTransformer(
    "jinaai/jina-embeddings-v5-text-small-retrieval",
    model_kwargs={"dtype": torch.bfloat16},
    trust_remote_code=True
)
    
def get_token_length(text):
    output = _embedding_model.encode(text)
    token_count = len(output)
    return token_count


def _get_hidden_states(text):
    transformer =_embedding_model[0]  
    tokenizer = transformer.tokenizer
    auto_model = transformer.auto_model
    
    inputs = tokenizer(text, return_tensors='pt', padding=True, truncation=True,return_offsets_mapping=True)
    inputs = inputs.to('cuda')
  
    with torch.no_grad():
        outputs = auto_model(**inputs, output_hidden_states=True)
   
    return outputs.last_hidden_state


def _create_embedding(query):
    query_embeddings = _embedding_model.encode(query)
    return query_embeddings


def _get_similarities(emb1,emb2):
    similarities = _embedding_model.similarity(emb1,emb2)
    return similarities