# System Architecture

Focused to establish a simplicstic RAG and CAG system.

```mermaid
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

    classDef frontend fill:#d0e1f9,stroke:#333;
    classDef backend fill:#e1f9d0,stroke:#333;
    classDef storage fill:#f9e1d0,stroke:#333;

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