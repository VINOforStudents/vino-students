"""Welcome to Reflex! This file outlines the steps to create a basic app."""

import reflex as rx
from rxconfig import config
from vino_students.state import State
from vino_students import style


def chat() -> rx.Component:
    """Renders the chat history as a list of question-answer pairs."""
    return rx.box(
        rx.foreach(
            State.chat_history,
            lambda messages: qa(messages[0], messages[1]),
        )
    )


def qa(question: str, answer: str) -> rx.Component:
    """Renders a single question-answer pair."""
    return rx.box(
        rx.box(
            # Change rx.text to rx.markdown for the question
            rx.markdown(question, style=style.question_style),
            text_align="right",
        ),
        rx.box(
            # Change rx.text to rx.markdown for the answer
            rx.markdown(answer, style=style.answer_style),
            text_align="left",
        ),
        margin_y="1em",
        width="100%",
    )


def action_bar() -> rx.Component:
    """Renders the question input field and send button."""
    return rx.hstack(
        rx.input(
            value=State.question,
            placeholder="Ask a question",
            on_change=State.set_question,
            style=style.input_style,
        ),
        rx.button(
            "Send",
            on_click=State.answer,
            style=style.button_style,
        ),
    )


def file_upload_area() -> rx.Component:
    """Renders the file upload component."""
    return rx.upload(
        rx.vstack(
            rx.button("Select File(s)"),
            rx.text("Drag and drop files here or click to select files."),
        ),
        id="my_upload",
        border="1px dotted rgb(107,114,128)",
        padding="2em",
        width="40em",
        margin_top="1em",
        margin_bottom="1em",
        on_drop=State.handle_upload(rx.upload_files()),
    )


def status_indicators() -> rx.Component:
    """Renders loading spinner and error messages."""
    return rx.cond(
        State.is_loading,
        rx.spinner(size="2"),
        rx.text(
            State.error_message, 
            color="red", 
            margin_top="0.5em", 
            display=rx.cond(State.error_message != "", "block", "none")
        )
    )


def clear_history_button() -> rx.Component:
    """Renders the clear history button fixed in the top right corner."""
    return rx.button(
        "Clear History",
        on_click=State.clear_chat_history,
        color_scheme="red",
        size="2",
        variant="outline",
        position="fixed",
        top="1em",
        right="1em",
        z_index="999",  # Ensures button stays on top of other content
    )


def index() -> rx.Component:
    """The main page component."""
    return rx.box(
        # Header with clear button
        clear_history_button(),
        
        # Main container
        rx.container(
            rx.vstack(
                # Chat section
                chat(),
                rx.spacer(),
                
                # Input section
                action_bar(),
                
                # File upload section
                file_upload_area(),
                
                # Status indicators
                status_indicators(),
                
                # Layout properties
                align="center",
                height="100vh",
                spacing="4",
            ),
        ),
        width="100%",
    )


# Initialize app
app = rx.App()
app.add_page(index)