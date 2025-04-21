from pydantic import BaseModel, Field
from typing import List

#------------------------------------------------------------------------------
# DATA MODELS
#------------------------------------------------------------------------------

class DocumentMetadata(BaseModel):
    """Metadata for a document chunk."""
    source: str
    filename: str
    chunk: int

class DocumentChunk(BaseModel):
    """A chunk of text with its metadata and ID."""
    text: str
    metadata: DocumentMetadata
    id: str

class ProcessingResult(BaseModel):
    """Results from processing a document."""
    documents: List[str] = Field(default_factory=list)
    metadatas: List[DocumentMetadata] = Field(default_factory=list)
    ids: List[str] = Field(default_factory=list)
    chunk_count: int = 0

class ChatRequest(BaseModel):
    question: str

class ChatResponse(BaseModel):
    answer: str