import reflex as rx
#import google.generativeai as genai
import os
import asyncio
import httpx  # May not be strictly needed if reflex manages the event loop

# --- Google GenAI Configuration ---
# Ensure the Google API Key is set in your environment variables
# e.g., export GOOGLE_API_KEY='YOUR_API_KEY'
# This configuration should ideally run once when your application starts.
# try:
#     api_key = os.environ.get("GOOGLE_API_KEY")
#     if not api_key:
#         raise ValueError(
#             "🔴 Error: GOOGLE_API_KEY environment variable not set. "
#             "Please set it and restart the application."
#         )
#     genai.configure(api_key=api_key)
#     print("✅ Google GenAI configured successfully.")
# except Exception as e:
#     print(f"🔴 Error configuring Google GenAI: {e}")
#     # You might want to prevent the app from fully starting or show an error state
#     # depending on your application's requirements.

BACKEND_API_URL = "http://127.0.0.1:8000"
# ---------------------------------

class State(rx.State):
    """The app state."""
    # Maximum number of entries to keep in chat history
    MAX_HISTORY_LENGTH = 10  
    
    # The current question being asked.
    question: str = "" # Initialize with an empty string

    # Keep track of the chat history as a list of (question, answer) tuples.
    chat_history: list[tuple[str, str]] = []

     is_loading: bool = False
    error_message: str = ""

    def set_question(self, question: str):
         self.question = question

    @rx.event
    def clear_chat_history(self):
         self.chat_history = []
         self.error_message = "" # Clear errors too
         return

    @rx.event
    async def answer(self):
         if not self.question or not self.question.strip():
             print("❓ Question is empty, skipping API call.")
             return

         # Indicate loading and clear previous errors
         self.is_loading = True
         self.error_message = ""
         yield # Update UI to show loading state

         question_to_send = self.question
         # Add placeholder while waiting for the backend
         placeholder_answer = "..."
         self.chat_history.append((question_to_send, placeholder_answer))
         self.question = "" # Clear input field
         yield # Update UI

         try:
             # --- Call your FastAPI backend ---
             async with httpx.AsyncClient() as client:
                 response = await client.post(
                     f"{BACKEND_API_URL}/chat", # Your chat endpoint
                     json={"question": question_to_send}, # Match backend's ChatRequest model
                     timeout=30.0 # Add a reasonable timeout
                 )
                 response.raise_for_status() # Raise exception for 4xx/5xx errors

                 response_data = response.json() # Get JSON response
                 backend_answer = response_data.get("answer", "Error: No answer received.")

                 # Update the placeholder answer with the actual one
                 self.chat_history[-1] = (question_to_send, backend_answer)

         except httpx.HTTPStatusError as e:
             # Handle HTTP errors (e.g., 404, 500) from backend
             error_detail = e.response.json().get("detail", e.response.text)
             print(f"🔴 HTTP error calling backend: {e.response.status_code} - {error_detail}")
             self.error_message = f"Error: {error_detail}"
             self.chat_history[-1] = (question_to_send, f"Error: Failed to get response ({e.response.status_code})")
         except httpx.RequestError as e:
             # Handle network errors (e.g., connection refused)
             print(f"🔴 Network error calling backend: {e}")
             self.error_message = "Error: Could not connect to the backend service."
             self.chat_history[-1] = (question_to_send, "Error: Connection failed.")
         except Exception as e:
             # Handle other unexpected errors
             print(f"🔴 Unexpected error in answer handler: {e}")
             self.error_message = "An unexpected error occurred."
             self.chat_history[-1] = (question_to_send, "Error: An unexpected error occurred.")
         finally:
             # Stop loading indicator regardless of success or failure
             self.is_loading = False
             yield # Update UI

     # --- Add File Upload Handler ---
     async def handle_upload(self, files: list[rx.UploadFile]):
         """Handle files uploaded via rx.upload."""
         self.is_loading = True # Show loading indicator
         self.error_message = ""
         yield

         upload_results = []
         async with httpx.AsyncClient() as client:
             for file in files:
                 try:
                     # Read file content provided by Reflex
                     file_content = await file.read()

                     # Send file to backend /upload endpoint
                     response = await client.post(
                         f"{BACKEND_API_URL}/upload",
                         files={"file": (file.filename, file_content, file.content_type)},
                         timeout=60.0 # Allow more time for uploads
                     )
                     response.raise_for_status()

                     # Add success message (you could display this in the UI)
                     result_detail = response.json().get("detail", f"Uploaded {file.filename}")
                     upload_results.append(result_detail)
                     print(f"✅ {result_detail}")

                 except httpx.HTTPStatusError as e:
                     error_detail = e.response.json().get("detail", e.response.text)
                     print(f"🔴 HTTP error uploading {file.filename}: {e.response.status_code} - {error_detail}")
                     self.error_message = f"Error uploading {file.filename}: {error_detail}"
                     upload_results.append(f"Error uploading {file.filename}")
                     # Optionally break or continue on error
                 except Exception as e:
                     print(f"🔴 Error processing upload {file.filename}: {e}")
                     self.error_message = f"Error uploading {file.filename}."
                     upload_results.append(f"Error uploading {file.filename}")

         self.is_loading = False
         # Optionally update UI with upload_results details
         yield
