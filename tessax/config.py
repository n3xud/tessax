from pydantic_settings import BaseSettings
from enum import Enum, auto

class ChunkModes(Enum):
    """Enum for different chunk modes."""

    SEMANTIC_CHUNKING = auto()
    LATE_CHUNKING = auto()    
    


class RAGConfig(BaseSettings):
    index_name : str = "test"
    chunk_size : int = 5
    simil : float  = 0.45
    
    add_parent_context : bool = True
    
    
    add_sibling_context : bool = True
    top_siblings : int = 3
    
    
    
    title : bool = True
    stay_on_domain : bool = True
    recursive : bool = False
    question_count:int = 10
    
    class Config:
        env_file = ".env"


config = RAGConfig()
