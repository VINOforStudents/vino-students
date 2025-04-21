# Standard library imports
import os
import shutil

# Third-party imports
import uvicorn
from fastapi import FastAPI, File, UploadFile, HTTPException

# Local application imports (after refactoring)
from config import USER_UPLOADS_DIR # Configuration constant
from database import initialize_vector_db # Function to setup DB
from document_processor import load_user_document # Function to process uploaded files
from llm_interaction import query_and_respond, chain, prompt, model # Function to interact with LLM
from file_utils import list_uploaded_files # Function to list files
from models import ChatRequest, ChatResponse # Pydantic models for request/response


# Initialize FastAPI App
app = FastAPI(
    title="LLM Conversation API",
    description="A simple API endpoint to interact with an LLM."
)

# Initialize database collections
try:
    collection_fw, collection_user = initialize_vector_db()
    chain = prompt | model
except Exception as e:
    print(f"FATAL: Could not initialize database or model: {e}")
    # In production, you might want to exit here with sys.exit(1)


@app.post("/chat", response_model=ChatResponse)
async def handle_chat(request: ChatRequest):
    conversation_history = []
    try:
        answer = query_and_respond(
            request.question, 
            conversation_history,
            collection_fw=collection_fw,
            collection_user=collection_user
        )
        if not answer:
            raise HTTPException(status_code=404, detail="Could not generate an answer.")
        return ChatResponse(answer=answer)
    except Exception as e:
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
