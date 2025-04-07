import reflex as rx
import httpx
import typing

# --- Configuration ---
# Define the URL of your running FastAPI backend endpoint
BACKEND_API_URL = "http://127.0.0.1:8000/conversation"

# --- Application State ---
class State(rx.State):
    """Manages the application's state."""

    # Input field content
    current_input: str = ""

    # List of tuples: (speaker: str, message: str)
    chat_history: list[tuple[str, str]] = []

    # Flag to indicate if waiting for API response
    is_loading: bool = False

    async def send_message(self):
        """Handles sending the user message to the backend API."""
        if not self.current_input.strip():
            # Don't send empty messages
            return

        # Immediately display the user's message
        user_msg = self.current_input
        self.chat_history.append(("User", user_msg))
        self.current_input = "" # Clear input field optimistically
        self.is_loading = True
        yield # Update UI before blocking for API call

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    BACKEND_API_URL,
                    json={"user_message": user_msg},
                    timeout=60.0 # Set a reasonable timeout (e.g., 60 seconds)
                )
                response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

                data = response.json()
                llm_response = data.get("llm_response", "Error: Invalid response format from API.")

        except httpx.TimeoutException:
            llm_response = "Error: The request to the backend API timed out."
        except httpx.RequestError as e:
            llm_response = f"Error: Could not connect to the backend API at {BACKEND_API_URL}. Is it running?\nDetails: {e}"
        except Exception as e:
            # Catch any other unexpected errors
            llm_response = f"An unexpected error occurred: {e}"
        finally:
            # Ensure loading state is turned off and AI response (or error) is added
            self.chat_history.append(("AI", llm_response))
            self.is_loading = False
            yield # Update UI with the AI's response and disable loading indicator


# --- UI Components ---

def message_bubble(speaker: str, text: str) -> rx.Component:
    """Creates a styled chat message bubble."""
    # Using rx.cond() for reactive conditional logic instead of Python if/else
    bg_color = rx.cond(
        speaker == "User",
        rx.color("accent", 3),
        rx.color("gray", 3)
    )
    text_align = rx.cond(
        speaker == "User",
        "right",
        "left"
    )
    align_self = rx.cond(
        speaker == "User",
        "flex-end",
        "flex-start"
    )

    return rx.box(
        rx.markdown( # Use markdown to render potential formatting from LLM
            text,
            color=rx.color("gray", 12), # Darker text
            white_space="pre-wrap" # Preserve whitespace and wrap text
        ),
        bg=bg_color,
        padding="0.75em",
        border_radius="lg",
        max_width="75%", # Limit bubble width
        align_self=align_self,
        text_align=text_align,
    )

def chat_interface() -> rx.Component:
    """Builds the main chat interface UI."""
    return rx.container( # Use a container for centering and max_width
        rx.vstack(
            # Chat history display area
            rx.box(
                rx.foreach(
                    State.chat_history,
                    lambda msg: message_bubble(msg[0], msg[1])
                ),
                width="100%",
                height="70vh", # Set a fixed height for the chat area
                overflow_y="auto", # Make it scrollable
                padding_y="1em",
                border=f"1px solid {rx.color('gray', 6)}",
                border_radius="md",
                display="flex",
                flex_direction="column",
                gap="0.75em" # Space between messages
            ),
            # Input area
            rx.hstack(
                rx.input(
                    placeholder="Type your message here...",
                    value=State.current_input,
                    on_change=State.set_current_input,
                    # Optional: Send message on pressing Enter
                    on_key_down=lambda event: rx.cond(
                        event == "Enter",
                        State.send_message(),
                        None
                    ),
                    flex_grow=1, # Make input field expand
                    variant="surface", # Use theme styling
                    size="3" # Larger size
                ),
                rx.button(
                    "Send",
                    on_click=State.send_message,
                    is_loading=State.is_loading,
                    # Disable button if loading or input is empty/whitespace only
                    is_disabled=State.is_loading | (State.current_input.strip() == ""),
                    size="3" # Larger size
                ),
                width="100%",
                padding_top="1em",
                align_items="center" # Align input and button vertically
            ),
            width="100%",
            align_items="stretch", # Stretch children horizontally
            spacing="5" # Spacing between chat area and input area
        ),
        padding_y="2em", # Add padding top/bottom for the whole container
        max_width="800px", # Set a max width for the chat interface
    )

# --- App Setup ---
# Create the app instance.
app = rx.App(
    theme=rx.theme(
        appearance="light", # or "dark" or "system"
        accent_color="blue", # Choose an accent color
        radius="medium" # Controls border radius
    )
)

# Add the main chat page.
app.add_page(chat_interface, route="/")

# Note: We don't call app.compile() here. Compilation happens via `reflex run`.