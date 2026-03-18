from pydantic import BaseModel
from enum import Enum, auto
from typing import List


class ChunkModes(Enum):
    """Enum for different chunk modes."""

    BASE_CHUNKING = auto()
    SENTENCE_CHUNKING = auto()
    SEMANTIC_CHUNKING = auto()
    CONTEXTUAL_CHUNKING = auto()


class Source(BaseModel):
    url: str
    recursive: bool = False


class Settings(BaseModel):
    chunk_size: int | None = 1000
    chunks_overlap: int | None = 100
    title: bool | None = False


class SourceList(BaseModel):
    index_name: str
    index_type: ChunkModes = ChunkModes.BASE_CHUNKING

    source: List[Source]
