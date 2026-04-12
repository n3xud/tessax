from pydantic import BaseModel
from enum import Enum, auto

class ChunkModes(Enum):
    """Enum for different chunk modes."""

    SEMANTIC_CHUNKING = auto()
    LATE_CHUNKING = auto()    
    
class RAGConfig(BaseModel):
    
    index_name : str = "test"
    chunk_size : int = 20
    chunk_overlap : int = 20
    splitting_type : ChunkModes = ChunkModes.SEMANTIC_CHUNKING
    
    title : bool = True
    stay_on_domain : bool = True
    recursive : bool = False
    