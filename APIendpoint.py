# Standard library imports
import os
import shutil
import sys

# Third-party imports
import uvicorn
from fastapi import FastAPI, UploadFile, File, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
import socketio
import prompts


# Local application imports (after refactoring)
from config import USER_UPLOADS_DIR, NEW_USER_UPLOADS_DIR # Configuration constant
from database import initialize_vector_db # Function to setup DB
from document_processor import load_documents_from_directory # Function to process uploaded files
from llm_interaction import query_and_respond# Function to interact with LLM
from file_utils import list_uploaded_files # Function to list files
from models import ChatRequest, ChatResponse # Pydantic models for request/response
from upload_supa import process_directory # Function to process directories
from upload_supa_chroma import upload_documents # Function to upload documents to ChromaDB

# Initialize FastAPI App
app = FastAPI(
    title="LLM Conversation API",
    description="A simple API endpoint to interact with an LLM."
)

# Initialize Socket.IO server
sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins="*",  # Allow all origins for development
    logger=True,
    engineio_logger=True
)

# Create Socket.IO ASGI application
socketio_app = socketio.ASGIApp(sio, app)

# Configure CORS
origins = [
    "http://localhost:3000",  # Default Reflex frontend port
    "http://127.0.0.1:3000", # Also allow this variant
    "http://localhost:*",     # Allow any localhost port for development
    "http://127.0.0.1:*",     # Allow any 127.0.0.1 port for development
    # Add any other origins if needed (e.g., your deployed frontend URL)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development - change this in production
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
        return ChatResponse(answer=answer)
    except Exception as e:
        print(f"Error in /chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error during chat processing: {str(e)}")

@app.post("/upload")
async def handle_upload(file: UploadFile = File(...)):
    if collection_user is None:
        raise HTTPException(
            status_code=503,
            detail="Database not available. The server failed to initialize properly."
        )
    
    os.makedirs(NEW_USER_UPLOADS_DIR, exist_ok=True)
    file_location = os.path.join(NEW_USER_UPLOADS_DIR, file.filename)
    try:
        # Save the uploaded file
        with open(file_location, "wb+") as file_object:
            shutil.copyfileobj(file.file, file_object)
        print(f"File {file.filename} uploaded to {file_location}")
        # Process the document
        content, metadata, ids, message = load_documents_from_directory(file_location, source="user_upload")
        print(f"Processed {file.filename} with message: {message}")
        if content is None:
            os.remove(file_location)
            raise HTTPException(status_code=400, detail=message)
        # Convert any list values in metadata to strings
        for doc_metadata in metadata:
            for key, value in doc_metadata.items():
                if isinstance(value, list):
                    doc_metadata[key] = ", ".join(str(item) for item in value)
                    
        # Add to user collection
        #collection_user.add(documents=content, metadatas=metadata, ids=ids)
        #print(f"About to process directory {NEW_USER_UPLOADS_DIR} -> {USER_UPLOADS_DIR}")

        # After successful processing, only process the directory with the new file
        try:
            success = upload_documents("user_upload")
            print(f"Result of upload_documents: {success}")
            if success:
                print("Successfully uploaded to Supabase")
            else:
                print("Failed to upload to Supabase")
        except Exception as e:
            print(f"Supabase upload error: {e}")
        
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
    try:
        file_list_string = list_uploaded_files(collection_user)
        return {"files_info": file_list_string}
    except Exception as e:
        print(f"Error in /list_files endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal server error listing files.")

# Socket.IO event handlers for Reflex compatibility
@sio.event
async def connect(sid, environ):
    print(f"Client {sid} connected")
    
@sio.event
async def disconnect(sid):
    print(f"Client {sid} disconnected")

@sio.event
async def event(sid, data):
    """Handle Reflex events"""
    print(f"Received event from {sid}: {data}")
    # Echo back the event - modify this based on your needs
    await sio.emit('event', {'delta': {}, 'events': []}, room=sid)

if __name__ == "__main__":
    uvicorn.run(socketio_app, host="127.0.0.1", port=8000)
