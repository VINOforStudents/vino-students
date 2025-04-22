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
    history: List[Dict[str, Any]]
    current_step: int

class ChatResponse(BaseModel):
    answer: str