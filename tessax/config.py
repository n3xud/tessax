from pydantic_settings import BaseSettings
from enum import Enum, auto
from typing import Literal

class ChunkModes(Enum):
    """Enum for different chunk modes."""

    SEMANTIC_CHUNKING = "semantic"
    FIXED_CHUNKING = "fixed"   
    
class VectorMode(Enum):
    
    NAIVE = "naive"

class RAGConfig(BaseSettings):
    index_name : str = "index_480"
    
    #Hyper
    chunk_size : int = 512
    simil : float  = 0.5
    retrieval_count : int = 5
    add_parent_context : bool = False
    
    
    question_count:int = 4
    recursive : bool = False
    chunk_mode : ChunkModes = ChunkModes.FIXED_CHUNKING
    
    use_gpt : bool = True

    
    add_sibling_context : bool = False
   
    title : bool = True
    
    
    
    
    class Config:
        env_file = ".env"


cfg = RAGConfig()

class RAGConfigTrial(BaseSettings):
    
    startup_trials : int = 5
    trials : int = 12
    fixed : bool = False
    study_name : str = "tpe_optimized"
    fixed_params : dict = {
                "chunk_mode": ChunkModes.SEMANTIC_CHUNKING.value,
                #"chunk_size": 512,  
                "simil": 0.6,
                "context_parents" : False,
                "retrieval_count" : 5,
                    
            }
    class Config:
        env_file = ".env"
        
cfg_trial = RAGConfigTrial()