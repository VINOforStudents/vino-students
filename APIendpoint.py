import os
import uvicorn
from fastapi import FastAPI, File, UploadFile, HTTPException
from pydantic import BaseModel
from fastapi import FastAPI, UploadFile, File, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any
import shutil
from main import (
    initialize_vector_db,
    query_and_respond,
    load_user_document,
    list_uploaded_files,
    model,
    USER_UPLOADS_DIR
)

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

# Initialize database collections
try:
    collection_fw, collection_user = initialize_vector_db()
except Exception as e:
    print(f"FATAL: Could not initialize database or model: {e}")
    # In production, you might want to exit here with sys.exit(1)

class ChatRequest(BaseModel):
    question: str
    history: List[Dict[str, Any]]
    current_step: int

class ChatResponse(BaseModel):
    answer: str

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
    os.makedirs(USER_UPLOADS_DIR, exist_ok=True)
    file_location = os.path.join(USER_UPLOADS_DIR, file.filename)
    try:
        # Save the uploaded file
        with open(file_location, "wb+") as file_object:
            shutil.copyfileobj(file.file, file_object)

        # Process the document
        docs, metas, ids, message = load_user_document(file_location)

        if docs is None:
            os.remove(file_location)
            raise HTTPException(status_code=400, detail=message)

        # Add to user collection
        collection_user.add(documents=docs, metadatas=metas, ids=ids)
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
        file_list_string = list_uploaded_files()
        return {"files_info": file_list_string}
    except Exception as e:
        print(f"Error in /list_files endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal server error listing files.")
