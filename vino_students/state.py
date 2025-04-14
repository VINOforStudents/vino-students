import reflex as rx
import google.generativeai as genai
import os
import asyncio # May not be strictly needed if reflex manages the event loop

# --- Google GenAI Configuration ---
# Ensure the Google API Key is set in your environment variables
# e.g., export GOOGLE_API_KEY='YOUR_API_KEY'
# This configuration should ideally run once when your application starts.
try:
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError(
            "🔴 Error: GOOGLE_API_KEY environment variable not set. "
            "Please set it and restart the application."
        )
    genai.configure(api_key=api_key)
    print("✅ Google GenAI configured successfully.")
except Exception as e:
    print(f"🔴 Error configuring Google GenAI: {e}")
    # You might want to prevent the app from fully starting or show an error state
    # depending on your application's requirements.

# ---------------------------------

class State(rx.State):
    """The app state."""
    # Maximum number of entries to keep in chat history
    MAX_HISTORY_LENGTH = 10  
    
    # The current question being asked.
    question: str = "" # Initialize with an empty string

    # Keep track of the chat history as a list of (question, answer) tuples.
    chat_history: list[tuple[str, str]] = []

    # Note: set_question is usually not needed if you bind the input field directly
    # to self.question using rx.Input(value=State.question, on_change=State.set_question)
    # or preferably just rx.Input(value=State.question, on_change=State.set_question) -> State.question
    # Let's keep it for now if you have a specific use case.
    def set_question(self, question: str):
        """Set the question."""
        self.question = question

    @rx.event
    def clear_chat_history(self):
        """Clear the entire chat history to free up memory."""
        self.chat_history = []
        return

    @rx.event
    async def answer(self):
        """
        Processes the user question, streams response from Gemini, updates history.
        This replaces the previous placeholder 'answer' method.
        """
        # Immediately return if the question is empty or whitespace only
        if not self.question or not self.question.strip():
            print("❓ Question is empty, skipping API call.")
            return

        # Trim chat history if it exceeds maximum length
        if len(self.chat_history) >= self.MAX_HISTORY_LENGTH:
            # Keep only the most recent entries
            self.chat_history = self.chat_history[-(self.MAX_HISTORY_LENGTH-1):]
            
        question_to_log = self.question # Store before clearing the input field
        print(f"Processing question: {question_to_log}")

        # Add a placeholder answer to the history immediately
        # Use a temporary marker or empty string for the answer part
        placeholder_answer = "..." # Or simply ""
        self.chat_history.append((question_to_log, placeholder_answer))

        # Clear the question input field on the frontend
        self.question = ""

        # Yield state update to clear input and show placeholder before API call
        yield

        # --- Asynchronous Gemini API Call ---
        try:
            # 1. Get the generative model instance
            # Using gemini-1.5-flash as a capable and fast default
            model = genai.GenerativeModel("gemini-1.5-flash-latest")

            # 2. Prepare generation configuration (optional)
            generation_config = genai.types.GenerationConfig(
                temperature=0.7,
                max_output_tokens=1024,  # Limit token size to prevent memory issues
                # You can add other parameters like:
                # stop_sequences=["\n\n", "---"]
            )

            # 3. Start the asynchronous streaming call
            print("📡 Calling Gemini API...")
            stream = await model.generate_content_async(
                question_to_log, # Use the stored question
                generation_config=generation_config,
            )
            print("✅ Stream started.")

            # 4. Process the stream chunk by chunk
            accumulated_answer = ""
            async for chunk in stream:
                # Check if the chunk contains text (safer access)
                if hasattr(chunk, 'text') and chunk.text:
                    accumulated_answer += chunk.text
                    # Update the last entry in chat_history with the streamed content
                    self.chat_history[-1] = (
                        question_to_log,
                        accumulated_answer,
                    )
                    yield # Yield to update the frontend progressively

            print("✅ Stream finished.")

        except Exception as e:
            # Handle potential API errors or other issues during generation
            print(f"🔴 An error occurred during Gemini API call: {e}")
            # Update the placeholder answer with an error message
            error_message = f"Error: Could not get response. ({e})"
            # Ensure we are updating the correct entry if history changed unexpectedly
            # (though with yield, it should be the last one)
            if self.chat_history and self.chat_history[-1][0] == question_to_log:
                 self.chat_history[-1] = (question_to_log, error_message)
            else:
                 # This case is unlikely if placeholder was added correctly
                 self.chat_history.append((question_to_log, error_message))
            yield # Yield to update UI with the error message
        # --- End Asynchronous Gemini API Call ---