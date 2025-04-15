"""Welcome to Reflex! This file outlines the steps to create a basic app."""

import reflex as rx
from rxconfig import config
from vino_students.state import State
from vino_students import style
import httpx

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
            rx.spacer(),  # This pushes the elements below it to the bottom
            action_bar(),
            rx.upload(
                id="my_upload",
                text="Upload a file",
                width="20%",
                margin_top="1em",
                margin_bottom="1em",
            ),
            align="center",
            height="100vh",  # Make the vstack take full viewport height
            spacing="4",
        ),
        align="center",
    )

app = rx.App()
app.add_page(index)