import os
import glob
from pydantic import BaseModel, Field
from typing import List, Optional

import chromadb
import chromadb.utils.embedding_functions as embedding_functions
import PyPDF2
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

# Constants and Configuration
CHROMA_DB_PATH = os.path.join(os.getcwd(), "chromadb")
DOCUMENTS_DIR = os.path.join(os.getcwd(), "documents")
USER_UPLOADS_DIR = os.path.join(os.getcwd(), "user_uploads")  # Directory for user uploads
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# Pydantic models for data validation
class DocumentMetadata(BaseModel):
    source: str
    filename: str
    chunk: int

class DocumentChunk(BaseModel):
    text: str
    metadata: DocumentMetadata
    id: str

class ProcessingResult(BaseModel):
    documents: List[str] = Field(default_factory=list)
    metadatas: List[DocumentMetadata] = Field(default_factory=list)
    ids: List[str] = Field(default_factory=list)
    chunk_count: int = 0

# Function to extract text from PDF
def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract text content from a PDF file.
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        Extracted text as a string
    """
    text = ""
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += page.extract_text() + "\n"
    except Exception as e:
        print(f"Error extracting text from PDF {pdf_path}: {e}")
    return text

# Function to process document content into chunks
def process_document_content(file_path: str, content: str, 
                            chunk_size: int = CHUNK_SIZE, 
                            chunk_overlap: int = CHUNK_OVERLAP) -> ProcessingResult:
    """
    Process document content into chunks with metadata and IDs.
    
    Args:
        file_path: Path to the source document
        content: Text content to be chunked
        chunk_size: Size of each chunk in characters
        chunk_overlap: Number of characters to overlap between chunks
        
    Returns:
        ProcessingResult containing document chunks, metadata, ids and chunk count
    """
    result = ProcessingResult()
    
    file_name = os.path.basename(file_path)
    doc_id_base = os.path.splitext(file_name)[0]
    
    # Skip if no content was extracted
    if not content.strip():
        print(f"Warning: No content extracted from {file_name}")
        return result
    
    # Implement fixed-size chunking
    start_index = 0
    chunk_number = 1
    while start_index < len(content):
        end_index = min(start_index + chunk_size, len(content))
        chunk = content[start_index:end_index]

        # Create DocumentMetadata object then convert to dict
        metadata = DocumentMetadata(
            source=file_path, 
            filename=file_name, 
            chunk=chunk_number
        ).model_dump()  # For newer Pydantic (v2)
        # Use .dict() instead if using Pydantic v1

        result.documents.append(chunk)
        result.metadatas.append(metadata)  # Store dict instead of Pydantic model
        result.ids.append(f"{doc_id_base}_chunk_{chunk_number}")

        start_index += chunk_size - chunk_overlap
        chunk_number += 1
    
    result.chunk_count = chunk_number - 1
    return result

# Function to read text files and PDFs from a directory
def load_documents_from_directory(directory_path):
    all_documents = []
    all_metadatas = []
    all_ids = []

    # Get all .txt and .pdf files in the directory
    txt_files = glob.glob(os.path.join(directory_path, "*.txt"))
    pdf_files = glob.glob(os.path.join(directory_path, "*.pdf"))
    file_paths = txt_files + pdf_files

    for file_path in file_paths:
        try:
            # Handle different file types
            if file_path.lower().endswith('.pdf'):
                content = extract_text_from_pdf(file_path)
            else:  # Assume it's a text file
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()

            # Process the document content
            result = process_document_content(file_path, content)
            
            all_documents.extend(result.documents)
            all_metadatas.extend(result.metadatas)
            all_ids.extend(result.ids)
            
            file_name = os.path.basename(file_path)
            print(f"Loaded {result.chunk_count} chunks from document: {file_name}")

        except Exception as e:
            print(f"Error loading {file_path}: {e}")

    return all_documents, all_metadatas, all_ids

def load_user_document(file_path):
    """Load a single document provided by the user."""
    try:
        # Handle different file types
        if file_path.lower().endswith('.pdf'):
            content = extract_text_from_pdf(file_path)
        elif file_path.lower().endswith(('.txt', '.md', '.py', '.js', '.html', '.css', '.json')):
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
        else:
            return None, None, None, f"Unsupported file type: {file_path}. Supported types are PDF and text files."

        # Process the document content
        result = process_document_content(file_path, content)
        
        if not result.documents:
            return None, None, None, f"No content extracted from {os.path.basename(file_path)}"
            
        return result.documents, result.metadatas, result.ids, f"Successfully processed {os.path.basename(file_path)} into {result.chunk_count} chunks"
    
    except Exception as e:
        return None, None, None, f"Error loading {file_path}: {str(e)}"

def add_results_to_context(results, section_title, context=""):
    """Add search results to the context string with proper formatting."""
    if results['documents'] and results['documents'][0]:
        context += f"\n--- {section_title} ---\n"
        for i, doc in enumerate(results['documents'][0]):
            source = results['metadatas'][0][i]['filename'] if 'metadatas' in results and results['metadatas'][0] else "Unknown source"
            context += f"\n--- From {source} ---\n{doc}\n"
        return context, True
    return context, False

def query_and_respond(query_text, conversation_history, collection=None):
    """Query collections and generate a response."""
    # Query frameworks collection
    fw_results = collection_fw.query(
        query_texts=[query_text],
        n_results=3  # Get top 3 from frameworks
    )
    
    # Query user collection
    user_results = collection_user.query(
        query_texts=[query_text],
        n_results=3  # Get top 3 from user docs
    )

    # Build conversation context from history
    conversation_context = ""
    if conversation_history:
        for entry in conversation_history:
            role = entry["role"]
            content = entry["content"]
            conversation_context += f"{role.capitalize()}: {content}\n"

    # Combine all retrieved document chunks into a comprehensive context
    combined_context = ""
    
    # Add both collections' results
    combined_context, has_fw_results = add_results_to_context(fw_results, "From Framework Documents", combined_context)
    combined_context, has_user_results = add_results_to_context(user_results, "From Your Documents", combined_context)
    
    # If we have context, generate a response
    if has_fw_results or has_user_results:
        response = chain.invoke({
            "context": combined_context,
            "history": conversation_context,
            "question": query_text
        })
        return response.content
    else:
        return "No relevant information found. Please try a different question."

def process_command(command):
    """Process special commands."""
    if command.startswith("/upload") or command.startswith("/add"):
        # Extract file path from command if provided
        parts = command.split(" ", 1)
        if len(parts) > 1 and parts[1].strip():
            file_path = parts[1].strip()
            return upload_file(file_path)
        else:
            # Prompt for file path
            file_path = input("Enter the path to the file you want to upload: ")
            return upload_file(file_path)
    elif command.startswith("/list"):
        return list_uploaded_files()
    elif command.startswith("/process"):
        return process_uploaded_files()
    
    return None  # Not a command

def list_uploaded_files():
    """List all files that have been uploaded by the user."""
    if not os.path.exists(USER_UPLOADS_DIR) or not os.listdir(USER_UPLOADS_DIR):
        return "No files have been uploaded yet."
    
    files = os.listdir(USER_UPLOADS_DIR)
    
    # Get the details from the collection
    user_docs = {}
    try:
        all_ids = collection_user.get(include=["metadatas"])
        if all_ids and "metadatas" in all_ids:
            for metadata in all_ids["metadatas"]:
                if metadata and "filename" in metadata:
                    filename = metadata["filename"]
                    if filename not in user_docs:
                        user_docs[filename] = 0
                    user_docs[filename] += 1
    except Exception as e:
        return f"Error retrieving document information: {str(e)}"
    
    # Format the output
    result = "Uploaded files:\n"
    for file in files:
        chunks = user_docs.get(file, "Unknown")
        result += f"  - {file} ({chunks} chunks in database)\n"
    
    return result

def process_uploaded_files():
    """Process all files in the user_uploads directory that haven't been processed yet."""
    if not os.path.exists(USER_UPLOADS_DIR) or not os.listdir(USER_UPLOADS_DIR):
        return "No files found in the uploads directory."
    
    # Get all files in the user_uploads directory
    files = os.listdir(USER_UPLOADS_DIR)
    processed_count = 0
    error_count = 0
    results = []
    
    # Process each file
    for file_name in files:
        file_path = os.path.join(USER_UPLOADS_DIR, file_name)
        
        # Skip directories
        if os.path.isdir(file_path):
            continue
            
        # Process the file
        docs, metas, ids, message = load_user_document(file_path)
        
        if docs is None:
            results.append(f"Error: {message}")
            error_count += 1
        else:
            # Add to user collection
            try:
                collection_user.add(
                    documents=docs,
                    metadatas=metas,
                    ids=ids
                )
                results.append(f"Success: {message}")
                processed_count += 1
            except Exception as e:
                results.append(f"Error adding {file_name} to collection: {str(e)}")
                error_count += 1
    
    # Prepare result message
    if processed_count == 0 and error_count == 0:
        return "No compatible files found to process."
    
    summary = f"Processed {processed_count} files with {error_count} errors.\n"
    return summary + "\n".join(results)

def upload_file(file_path):
    """Upload a file to the user collection."""
    # Handle relative paths - convert to absolute
    if not os.path.isabs(file_path):
        file_path = os.path.join(os.getcwd(), file_path)
    
    if not os.path.exists(file_path):
        return f"File not found: {file_path}"
    
    # Create a copy in the user_uploads directory
    os.makedirs(USER_UPLOADS_DIR, exist_ok=True)
    file_name = os.path.basename(file_path)
    destination_path = os.path.join(USER_UPLOADS_DIR, file_name)
    
    try:
        # Copy the file to our uploads directory
        with open(file_path, 'rb') as src_file:
            with open(destination_path, 'wb') as dest_file:
                dest_file.write(src_file.read())
        print(f"Copied file to {destination_path}")
    except Exception as e:
        return f"Error copying file to uploads directory: {str(e)}"
    
    # Process the file
    docs, metas, ids, message = load_user_document(destination_path)
    
    if docs is None:
        return message
    
    # Add to user collection
    try:
        collection_user.add(
            documents=docs,
            metadatas=metas,
            ids=ids
        )
        return f"{message}. Added to your documents collection."
    except Exception as e:
        return f"Error adding document to collection: {str(e)}"

# def run_chat_interface():
#     print("Chat with Gemini 1.5 Pro (type 'exit' to quit)")
#     print("Special commands:")
#     print("  /upload or /add [filepath] - Upload a document (absolute or relative path)")
#     print("  /list - List all uploaded documents")
#     print("  /process - Process all files in the uploads directory")
#     print("-" * 50)

#     while True:
#         user_input = input("You: ")

#         if user_input.lower() == "exit":
#             print("Goodbye!")
#             break
            
#         # Check if this is a special command
#         if user_input.startswith("/"):
#             result = process_command(user_input)
#             if result:
#                 print(f"System: {result}")
#                 print("-" * 50)
#                 continue

#         # Get document context and response
#         answer = query_and_respond(user_input, conversation_history)

#         # Add this exchange to history
#         conversation_history.append({"role": "user", "content": user_input})
#         conversation_history.append({"role": "assistant", "content": answer})

#         print(f"Gemini: {answer}")
#         print("-" * 50)

# System prompt
prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are a helpful assistant that answers questions based on document context."
    ),
    (
        "human",
        """I have the following context:
        {context}

        Conversation history:
        {history}

        Answer my question: {question}"""
    )
])

def initialize_vector_db():
    """Initialize ChromaDB and load documents if needed."""
    client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
    google_ef = embedding_functions.GoogleGenerativeAiEmbeddingFunction(api_key=api_key)
    
    try:
        # Create or get the frameworks collection
        collection_fw = client.get_or_create_collection(
            name="frameworks", 
            embedding_function=google_ef
        )
        
        # Create or get the user documents collection
        collection_user = client.get_or_create_collection(
            name="user_documents",
            embedding_function=google_ef
        )
        
        # Process documents only if needed
        if collection_fw.count() == 0:
            print("Frameworks collection is empty. Loading documents...")
            docs, metas, ids = load_documents_from_directory(DOCUMENTS_DIR)
            
            # Add documents to collection if any were loaded
            if docs:
                collection_fw.add(
                    documents=docs,
                    metadatas=metas,
                    ids=ids
                )
                print(f"Added {len(docs)} document chunks to the frameworks collection.")
            else:
                print("No documents were loaded. Please check the directory path.")
        else:
            print(f"Using existing frameworks collection with {collection_fw.count()} document chunks.")
        
        print(f"User documents collection has {collection_user.count()} document chunks.")
        
        return collection_fw, collection_user
        
    except Exception as e:
        print(f"Error initializing ChromaDB collection: {e}")
        raise

# def main():
#     """Main application entry point."""
#     # Initialize the model and conversation
#     global collection_fw, collection_user, chain, conversation_history
    
#     collection_fw, collection_user = initialize_vector_db()
#     conversation_history = []
#     chain = prompt | model
    
#     # Start chat interface
#     run_chat_interface()
load_dotenv()
    
# Ensure upload directory exists
os.makedirs(USER_UPLOADS_DIR, exist_ok=True)

api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("API key not found. Please set the GOOGLE_API_KEY environment variable.")

model = ChatGoogleGenerativeAI(
    model="gemini-1.5-pro",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2
)
