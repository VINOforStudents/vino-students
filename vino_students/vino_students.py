"""Welcome to Reflex! This file outlines the steps to create a basic app."""

import reflex as rx
from rxconfig import config
from vino_students.state import State
from vino_students import style


def chat() -> rx.Component:
    return rx.box(
        rx.foreach(
            State.chat_history,
            lambda messages: qa(messages[0], messages[1]),
        )
    )

def qa(question: str, answer: str) -> rx.Component:
    return rx.box(
        rx.box(
            rx.text(question, style=style.question_style),
            text_align="right",
        ),
        rx.box(
            rx.text(answer, style=style.answer_style),
            text_align="left",
        ),
        margin_y="1em",
        width="100%",
    )

def action_bar() -> rx.Component:
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

def index() -> rx.Component:
    return rx.container(
        rx.vstack(
            chat(),
            rx.spacer(),
            action_bar(),
            # Configure the upload component
            rx.upload(
                rx.vstack(
                    rx.button("Select File(s)"),
                    rx.text("Drag and drop files here or click to select files."),
                ),
                id="my_upload",
                border="1px dotted rgb(107,114,128)",
                padding="2em",
                width="40em", # Match input width maybe?
                margin_top="1em",
                margin_bottom="1em",
                # --- Connect the upload handler ---
                on_drop=State.handle_upload(rx.upload_files()), # Call handler on drop/select
                # You might want multiple=True if allowing multiple uploads
            ),
            # Add loading/error indicators
            rx.cond(
                State.is_loading,
                rx.spinner(size="2"), 
                rx.text(State.error_message, color="red", margin_top="0.5em")
            ),
            align="center",
            height="100vh",
            spacing="4",
        ),
        align="center",
    )

app = rx.App()
app.add_page(index)