import google.generativeai as genai
import os
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field # Use Pydantic for data validation
from dotenv import load_dotenv

load_dotenv()
google_api_key = os.getenv("GOOGLE_API_KEY")
if not google_api_key:
     raise ValueError("Google API key not found. Make sure it's set in the .env file.")
genai.configure(api_key=google_api_key)
google_model = genai.GenerativeModel('gemini-2.0-flash')

class ConversationRequest(BaseModel):
    user_message: str
    history: list[dict[str, str]] = Field(default_factory=list) 

class ConversationResponse(BaseModel):
    llm_response: str


# --- Initialize FastAPI App ---
app = FastAPI(
    title="LLM Conversation API",
    description="A simple API endpoint to interact with an LLM."
)
# ----------------------------

# --- Define the Conversation Endpoint ---
@app.post("/conversation", response_model=ConversationResponse)
async def handle_conversation(request: ConversationRequest):
    """
    Receives a user message and returns the LLM's response.
    """
    print(f"Received message: {request.user_message}") # Log input for debugging

    try:
        # --- Interact with the chosen LLM ---

        response = await google_model.generate_content_async(request.user_message) # Use async version with FastAPI
        # Add error handling for blocked prompts if necessary
        if not response.parts:
             # Handle case where generation might be blocked or empty
             raise HTTPException(status_code=500, detail="LLM response generation failed or was blocked.")
        llm_output = response.text

        # -----------------------------------

        print(f"LLM Response: {llm_output}") # Log output for debugging
        return ConversationResponse(llm_response=llm_output.strip())

    except Exception as e:
        print(f"Error interacting with LLM: {e}") # Log the error
        # Consider more specific error handling for API errors vs internal errors
        raise HTTPException(status_code=500, detail=f"Error processing request: {e}")

# -----------------------------------
# --- Add a simple root endpoint for testing ---
@app.get("/")
async def root():
    return {"message": "LLM Conversation API is running. POST to /conversation"}
# --------------------------------------------

# --- Run the server (for development) ---
# This part allows running directly with `python main.py`
# For production, use `uvicorn main:app --host 0.0.0.0 --port 8000`
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
# ----------------------------------------