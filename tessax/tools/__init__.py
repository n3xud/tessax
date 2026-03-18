from sentence_transformers import SentenceTransformer
from tokenizers import Tokenizer

tokenizer = Tokenizer.from_pretrained("Qwen/Qwen3-0.6B")
model = SentenceTransformer("Qwen/Qwen3-Embedding-0.6B", local_files_only=True)
