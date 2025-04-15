# System Architecture

Focused to establish a simplicstic RAG and CAG system.

```mermaid
---
config:
    layout: default
    look: handDrawn
    theme: dark
---
graph TD
    subgraph "Frontend"
        GUI[Reflex Web GUI]
        CLI[Python CLI]
    end

    subgraph "Backend Services"
        VDB[ChromaDB Vector Database]
        LLM[Gemini 1.5 Pro LLM]
        DOC[Document Processor]
    end

    subgraph "Storage"
        FW[Framework Documents]
        UD[User Documents]
        VS[Vector Storage]
    end

    GUI --> DOC
    CLI --> DOC
    DOC --> VDB
    VDB --> VS
    FW --> DOC
    UD --> DOC
    VDB <--> LLM
    GUI --> UD

    class GUI,CLI frontend;
    class VDB,LLM,DOC backend;
    class FW,UD,VS storage;
```

## Component Description

| Component          | Description                  | Technology                 |
| ------------------ | ---------------------------- | -------------------------- |
| Web GUI            | User interface               | Reflex (Python)            |
| CLI                | Command-line interface       | Python                     |
| Vector Database    | Document storage & retrieval | ChromaDB                   |
| LLM                | Language model for Q&A       | Google Gemini 1.5 Pro      |
| Document Processor | PDF/text processing          | PyPDF2, LangChain          |
| Storage            | File & vector storage        | Local filesystem, ChromaDB |

## Data Flow

1. User interacts via GUI or CLI
2. Documents are processed and chunked
3. Text chunks are converted to vectors
4. Vectors are stored in ChromaDB
5. User queries trigger similarity search
6. Relevant context is sent to LLM
7. LLM generates response
// ...existing code...

## Sequence Diagram

```mermaid
sequenceDiagram
    actor User
    participant GUI as Web GUI/CLI
    participant DOC as Document Processor
    participant VDB as ChromaDB
    participant LLM as Gemini 1.5 Pro

    %% Document Upload Flow
    User->>GUI: Upload Document
    GUI->>DOC: Process Document
    DOC->>DOC: Chunk Text
    DOC->>VDB: Store Vectors
    VDB-->>GUI: Confirm Storage

    %% Query Flow
    User->>GUI: Ask Question
    GUI->>VDB: Search Similar Vectors
    VDB-->>GUI: Return Relevant Context
    GUI->>LLM: Generate Response
    LLM-->>GUI: Return Answer
    GUI-->>User: Display Response
```

This sequence diagram illustrates two main flows:
1. Document Upload Process
2. Query and Response Generation

The diagram shows how components interact in a time-ordered sequence, making it clear how data flows through the system during different operations.