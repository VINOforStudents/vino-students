import reflex as rx
from rxconfig import config
from vino_students.state import State
from vino_students import style


def chat() -> rx.Component:
    """Renders the chat history as a list of question-answer pairs with auto-scrolling."""
    return rx.box(
        rx.foreach(
            State.chat_history,
            lambda messages: qa(messages[0], messages[1]),
        ),
        rx.script(
            """
            // Auto-scroll to bottom of chat container
            function scrollToBottom() {
                const chatContainer = document.getElementById('chat-container');
                if (chatContainer) {
                    chatContainer.scrollTop = chatContainer.scrollHeight;
                }
            }
            
            // Run on load and whenever content changes
            scrollToBottom();
            setTimeout(scrollToBottom, 100); // Run again after a short delay for content to render
            """,
            is_hydrate_event=True,
        ),
        id="chat-container", 
        margin_top="7em",
        width="45em",
        height="70vh",
        overflow="auto",
        #border="1px solid black",
        #border_radius="md",
        padding="1em",
        margin_bottom="1em",
    )


def qa(question: str, answer: str) -> rx.Component:
    """Renders a single question-answer pair."""
    return rx.box(
        rx.box(
            # Change rx.text to rx.markdown for the question
            rx.markdown(question, style=style.question_style, max_width="34vh"),
            text_align="right",
            
        ),
        rx.box(
            # Change rx.text to rx.markdown for the answer
            rx.markdown(answer, style=style.answer_style, max_width="34vh",),
            text_align="left",
        ),
        margin_y="1em",
        width="100%",
    
    )


def action_bar() -> rx.Component:
    """Renders the question input field and send button."""
    return rx.hstack(
        rx.text_area(  # Changed from rx.input to rx.text_area
            value=State.question,
            placeholder="Ask a question",
            color=rx.color("sand", 3),
            on_change=State.set_question,
            # Behavior of the "Enter" key:
            # Option 1: Keep "Enter" to submit the form (as it was with rx.input).
            # This will prevent "Enter" from creating a new line in the textarea.
            on_key_down=lambda key: rx.cond(
                key == "Enter",
                State.answer,
                rx.noop()
            ),
            
            rows=1, 
            
            # Controls manual resizing by the user. "vertical" allows vertical drag-to-resize.
            # "none" disables manual resizing if auto-sizing is preferred.
            resize="vertical", 
            width="100%", # Makes the textarea take the available width in the hstack
        ),
        rx.button(
            "Send",
            on_click=State.answer,
            style=style.button_style,
        ),
        width="45em",
        align_items="flex-end",  # Aligns the button to the bottom of the textarea as it grows
    )


def file_upload_area() -> rx.Component:
    """Renders the file upload component."""
    return rx.upload(
        rx.hstack(
            rx.button("Select File(s)",
                       style=style.button_style),
            rx.text("Drag and drop files here or click to select files.", color="gray"),
            width="100%",
            height="100%",
            #display="block",
            justify="start",
            align_items="center",
            spacing="3",
            padding="1em",
        ),
        id="my_upload",
        background_color="white",
        width="45em",
        height="5em",
        margin_top="1em",
        #margin_bottom="1em",
        on_drop=State.handle_upload(rx.upload_files()),
        size="2",
        #justify_content="center",
        #align_items="center",
        padding="1em",
        border="2px dotted #222221",
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
        color=rx.color("ruby", 3),
        border="3px solid ruby",
        size="2",
        variant="outline",
        position="fixed",
        top="8em",
        right="20em",
        z_index="999", 
    )

def navbar_link(
    url: str, 
    default_image_src: str, 
    active_image_src: str = None, 
    step_number: int = None, 
    text: str = None
) -> rx.Component:
    """Creates a navbar link with active/inactive states for navigation steps."""
    active_height = "0.5em" if step_number == 1 else "4em"
    
    if active_image_src and step_number is not None:
        # Link with active/inactive states
        return rx.link(
            rx.cond(
                State.active_step == step_number,
                # Active state
                rx.image(
                    src=active_image_src,
                    width="100%",
                    height="8em",
                    alt=text or f"Step {step_number}",
                    fit="contain",
                    background_color="white",
                ),
                # Inactive state
                rx.image(
                    src=default_image_src,
                    width="100%",
                    max_width="10em",
                    height=active_height,
                    alt=text or f"Step {step_number}",
                    fit="contain",
                    padding_x="3em",
                ),
            ),
            href=url,
            height="3.8em",
            width="25em",
            display="flex",
            align_items="center",
            on_click=State.set_active_step(step_number),
            justify_content="center",
            padding_x="0",
            border_left="1px solid #222221", 
            border_right="1px solid #222221",
            background_color="white",
        )
    elif default_image_src:
        # Image-only link
        return rx.link(
            rx.image(
                src=default_image_src,
                width="100%",
                max_width="20em",
                height=active_height,
                alt=text or "Navigation icon",
                fit="contain",
                border_left="1px solid #222221", 
                border_right="1px solid #222221",
                box_sizing="border-box",
                padding_x="3em",
                background_color="white",
            ),
            href=url,
            height="3.8em",
            width="25em",
            display="flex",
            align_items="center",
            justify_content="center",
        )
    else:
        # Text-only link
        return rx.link(
            rx.text(text, size="4", weight="medium"), 
            href=url
        )


def navbar() -> rx.Component:
    """Renders the navigation bar with step indicators."""
    return rx.box(
        rx.desktop_only(
            rx.hstack(
                rx.hstack(
                    navbar_link(url="/#", default_image_src="/step1.svg", active_image_src="/step1_active.png", step_number=1, text="Step 1"),
                    navbar_link(url="/#", default_image_src="/step2.svg", active_image_src="/step2_active.png", step_number=2, text="Step 2"),
                    navbar_link(url="/#", default_image_src="/step3.svg", active_image_src="/step3_active.png", step_number=3, text="Step 3"),
                    navbar_link(url="/#", default_image_src="/step4.svg", active_image_src="/step4_active.png", step_number=4, text="Step 4"),
                    navbar_link(url="/#", default_image_src="/step5.svg", active_image_src="/step5_active.png", step_number=5, text="Step 5"),
                    navbar_link(url="/#", default_image_src="/step6.svg", active_image_src="/step6_active.png", step_number=6, text="Step 6"),
                    justify="between",
                    spacing="0",
                    width="70%",
                ),
                width="100%",
                align_items="center",
                height="4em",
                padding="-0.2em",
                justify_content="center",
            ),
        ),
        bg="white",
        padding="0",
        position="fixed",
        top="2em",
        z_index="5",
        width="100%",
        border_top="1px solid #222221",
        border_bottom="1px solid #222221",
        height="4em",
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
                
                # Status indicators
                status_indicators(),
                
                # Spacer to push input elements to bottom
                rx.spacer(),
                
                # Input section and File upload moved to bottom
                action_bar(),
                file_upload_area(),

                navbar(),
                
                # Layout properties
                align="center",
                spacing="4",
                overflow_y="hidden",
                height="95vh",
                position="relative",
            ),
        ),
        width="100%",
        background_color="white",
    )



# Initialize app
app = rx.App()
app.add_page(index)