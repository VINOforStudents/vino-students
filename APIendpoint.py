# Standard library imports
import os
import shutil
import sys

# Third-party imports
import uvicorn
from fastapi import FastAPI, UploadFile, File, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
import prompts


# Local application imports (after refactoring)
from config import USER_UPLOADS_DIR, NEW_USER_UPLOADS_DIR # Configuration constant
from database import initialize_vector_db # Function to setup DB
from document_processor import load_user_document # Function to process uploaded files
from llm_interaction import query_and_respond# Function to interact with LLM
from file_utils import list_uploaded_files # Function to list files
from models import ChatRequest, ChatResponse # Pydantic models for request/response
from upload_supa import process_directory # Function to process directories

# Initialize FastAPI App
app = FastAPI(
    title="LLM Conversation API",
    description="A simple API endpoint to interact with an LLM."
)

# Configure CORS
origins = [
    "http://localhost:3000",  # Default Reflex frontend port
    "http://127.0.0.1:3000", # Also allow this variant
    # Add any other origins if needed (e.g., your deployed frontend URL)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

collection_fw = None
collection_user = None


try:
    collection_fw, collection_user = initialize_vector_db()
    if not collection_fw or not collection_user:
        raise Exception("Database collections were not properly initialized")
except Exception as e:
    print(f"FATAL: Could not initialize database or model: {e}")
    sys.exit(1)

@app.post("/chat", response_model=ChatResponse)
async def handle_chat(request: ChatRequest):
    """
    Handle chat requests by querying the LLM with the provided question and context.
    
    Args:
        request: ChatRequest containing question, history, and current step
        
    Returns:
        ChatResponse with the answer from the LLM
    """
    try:
        answer = query_and_respond(
            query_text=request.question,
            history_data=request.history,
            current_step=request.current_step,
            collection_fw=collection_fw,
            collection_user=collection_user
        )
        if not answer:
            raise HTTPException(status_code=404, detail="Could not generate an answer.")
        # Convert answer to string if it's not already
        if not isinstance(answer, str):
            answer = str(answer)
        return ChatResponse(answer=answer)
    except Exception as e:
        logger.error(f"Error in /chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error during chat processing: {str(e)}")

def process_metadata(metadata):
    """Convert any list values in metadata to comma-separated strings."""
    for doc_metadata in metadata:
        for key, value in doc_metadata.items():
            if isinstance(value, list):
                doc_metadata[key] = ", ".join(str(item) for item in value)
    return metadata


def save_uploaded_file(file, file_location):
    """Save the uploaded file to the specified location."""
    with open(file_location, "wb+") as file_object:
        shutil.copyfileobj(file.file, file_object)
    print(f"File {file.filename} uploaded to {file_location}")


def upload_to_supabase(new_dir, user_dir):
    """Process the directory and upload to Supabase."""
    try:
        success = process_directory(new_dir, user_dir)
        if success:
            print("Successfully uploaded to Supabase")
        else:
            print("Failed to upload to Supabase")
        return success
    except Exception as e:
        print(f"Supabase upload error: {e}")
        return False


@app.post("/upload")
async def handle_upload(file: UploadFile = File(...)):
    """
    Handle file uploads, process documents, and add them to the vector database.
    
    Args:
        file: The uploaded file
        
    Returns:
        Dict with detail message about the upload status
    """
    # Validate database is available
    if collection_user is None:
        raise HTTPException(
            status_code=503,
            detail="Database not available. The server failed to initialize properly."
        )
    
    # Create upload directory and set file path
    os.makedirs(NEW_USER_UPLOADS_DIR, exist_ok=True)
    file_location = os.path.join(NEW_USER_UPLOADS_DIR, file.filename)
    
    try:
        # Save the uploaded file
        save_uploaded_file(file, file_location)
        
        # Process the document
        metadata, content, message = load_user_document(file_location)
        print(f"Processed {file.filename} with message: {message}")
        
        # Handle processing failures
        if content is None:
            os.remove(file_location)
            raise HTTPException(status_code=400, detail=message)
        
        # Prepare metadata and add to vector database
        metadata = process_metadata(metadata)
        collection_user.add(documents=content, metadatas=metadata, ids=[file.filename])
        
        # Upload to Supabase
        print(f"Processing directory {NEW_USER_UPLOADS_DIR} -> {USER_UPLOADS_DIR}")
        upload_to_supabase(NEW_USER_UPLOADS_DIR, USER_UPLOADS_DIR)
        
        return {"detail": f"Successfully uploaded and processed {file.filename}. {message}"}
        
    except Exception as e:
        print(f"Error in /upload endpoint: {e}")
        if os.path.exists(file_location):
            os.remove(file_location)
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")
    finally:
        await file.close()

@app.get("/list_files")
async def get_uploaded_files():
    """
    List all uploaded files in the user collection.
    
    Returns:
        Dict with information about uploaded files
    """
    try:
        file_list_string = list_uploaded_files(collection_user)
        return {"files_info": file_list_string}
    except Exception as e:
        print(f"Error in /list_files endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal server error listing files.")