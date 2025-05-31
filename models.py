from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

from langchain_core.messages import HumanMessage, AIMessage, BaseMessage


#------------------------------------------------------------------------------
# APPLICATION STATE (In-Memory)
#------------------------------------------------------------------------------

conversation_history: List[BaseMessage] = []
current_process_step: int = 1 # Start at step 1
planner_details: Optional[str] = None # To store the plan generated in Step 3


#------------------------------------------------------------------------------
# DATA MODELS
#------------------------------------------------------------------------------

class ChunkMetadata(BaseModel):
    """A chunk of text with its metadata and ID."""
    id: str
    chunk_number: int
    chunk_length: int
    parent: Optional[str] = None  # Name of the section this chunk belongs to
    text: str

class DocumentMetadata(BaseModel):
    """Metadata for a document chunk."""
    source: str
    filename: str
    file_size: Optional[int] = None
    file_type: Optional[str] = None
    page_count: Optional[int] = None
    word_count: Optional[int] = None
    char_count: Optional[int] = None
    keywords: Optional[List[str]] = None
    abstract: Optional[str] = None

class ProcessingResult(BaseModel):
    """Results from processing a document."""
    documents: List[str] = Field(default_factory=list)
    metadatas: List[DocumentMetadata] = Field(default_factory=list)
    chunk_metadatas: List[ChunkMetadata] = Field(default_factory=list)
    chunk_count: int = Field(default_factory=lambda: 0)

    

class ChatRequest(BaseModel):
    question: str
    history: List[Dict[str, Any]]
    current_step: int

class ChatResponse(BaseModel):
    answer: str

class KBMetadata(BaseModel):
    """Metadata for a knowledge base document."""
    file_name: str
    file_size: int
    file_type: str
    page_count: int
    word_count: int
    char_count: int
    keywords: List[str]
    source: str
    abstract: str

class LargeObject(BaseModel):
    """A large object with metadata."""
    plain_text: str
    metadata: KBMetadata