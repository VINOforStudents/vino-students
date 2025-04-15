import google.generativeai as genai
import os
import uvicorn
from fastapi import FastAPI, File, UploadFile, HTTPException
from pydantic import BaseModel, Field # Use Pydantic for data validation
from dotenv import load_dotenv
import python_multipart
import shutil
from main import (
    initialize_vector_db,
    query_and_respond,
    load_user_document,
    list_uploaded_files,
    prompt,  # If needed globally
    model,   # If needed globally
    USER_UPLOADS_DIR # Import constants
)

try:
     collection_fw, collection_user = initialize_vector_db()
     # Assuming 'prompt' and 'model' are initialized correctly via imports or here
     # Make sure 'model' and 'prompt' from main.py are accessible
     chain = prompt | model
except Exception as e:
     print(f"FATAL: Could not initialize database or model: {e}")
     # Optionally, exit or prevent app startup
     # exit(1) # Uncomment if initialization failure should stop the server

class ChatRequest(BaseModel):
    question: str
    # history: list[dict[str, str]] = [] # Optional

class ChatResponse(BaseModel):
    answer: str


# --- Initialize FastAPI App ---
app = FastAPI(
    title="LLM Conversation API",
    description="A simple API endpoint to interact with an LLM."
)
# ----------------------------


@app.post("/chat", response_model=ChatResponse)
async def handle_chat(request: ChatRequest):
    conversation_history = [] # Manage history as needed
    try:
        # Call the imported function
        answer = query_and_respond(request.question, conversation_history, collection_fw, collection_user)
        if not answer:
            raise HTTPException(status_code=404, detail="Could not generate an answer.")
        return ChatResponse(answer=answer)
    except Exception as e:
         # Log the error for debugging
         print(f"Error in /chat endpoint: {e}")
         raise HTTPException(status_code=500, detail="Internal server error during chat processing.")


@app.post("/upload")
async def handle_upload(file: UploadFile = File(...)):
    os.makedirs(USER_UPLOADS_DIR, exist_ok=True)
    file_location = os.path.join(USER_UPLOADS_DIR, file.filename)
    try:
        # Save the uploaded file
        with open(file_location, "wb+") as file_object:
            shutil.copyfileobj(file.file, file_object)

        # Call the imported function to process
        docs, metas, ids, message = load_user_document(file_location)

        if docs is None:
            os.remove(file_location)
            raise HTTPException(status_code=400, detail=message)

        # Add to user collection (ensure collection_user is accessible)
        collection_user.add(documents=docs, metadatas=metas, ids=ids)
        return {"detail": f"Successfully uploaded and processed {file.filename}. {message}"}

    except Exception as e:
         # Log the error
         print(f"Error in /upload endpoint: {e}")
         # Clean up saved file if error occurs
         if os.path.exists(file_location):
             os.remove(file_location)
         raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")
    finally:
         await file.close()


@app.get("/list_files")
async def get_uploaded_files():
     try:
          # Call the imported function
          file_list_string = list_uploaded_files()
          return {"files_info": file_list_string}
     except Exception as e:
          # Log the error
          print(f"Error in /list_files endpoint: {e}")
          raise HTTPException(status_code=500, detail="Internal server error listing files.")
