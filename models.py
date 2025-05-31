from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from enum import Enum

from langchain_core.messages import HumanMessage, AIMessage, BaseMessage

class FileType(str, Enum):
    PDF = "pdf"
    DOCX = "docx"
    TXT = "txt"
    MD = "md"

#------------------------------------------------------------------------------
# APPLICATION STATE (In-Memory)
#------------------------------------------------------------------------------

conversation_history: List[BaseMessage] = []
current_process_step: int = 1 # Start at step 1
planner_details: Optional[str] = None # To store the plan generated in Step 3


#------------------------------------------------------------------------------
# DATA MODELS
#------------------------------------------------------------------------------

class DocumentMetadata(BaseModel):
    """A document chunk with its ID and metadata."""
    id: str
    chunk_number: int
    chunk_length: int
    parent: Optional[str] = None  # Name of the section this chunk belongs to

class DocumentChunk(BaseModel):
    """A document chunk combining content and metadata."""
    metadata: DocumentMetadata
    text: str = Field(..., min_length=1)

class FileMetadata(BaseModel):
    """Metadata for a file."""
    source: str = Field(..., min_length=1)
    filename: str = Field(..., min_length=1)
    file_size: int = Field(..., ge=0)
    file_type: FileType
    page_count: int
    word_count: int
    char_count: int
    keywords: List[str]
    source: str
    abstract: str

class ProcessingResult(BaseModel):
    """Results from processing a document."""
    ids: List[str] = Field(default_factory=list)
    documents: List[str] = Field(default_factory=list)
    doc_metadatas: List[DocumentMetadata] = Field(default_factory=list)
    file_metadatas: FileMetadata
    chunk_count: int = Field(default=0, ge=0)
    
class ChatRequest(BaseModel):
    question: str
    history: List[Dict[str, Any]]
    current_step: int

class ChatResponse(BaseModel):
    answer: str

# class KBMetadata(BaseModel):
#     """Metadata for a knowledge base document."""
#     file_name: str
#     file_size: int
#     file_type: str
#     page_count: int
#     word_count: int
#     char_count: int
#     keywords: List[str]
#     source: str
#     abstract: str

# class LargeObject(BaseModel):
#     """A large object with metadata."""
#     plain_text: str
#     metadata: FileMetadata