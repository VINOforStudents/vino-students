import reflex as rx



shadow = "rgba(0, 0, 0, 0.15) 0px 2px 8px"
chat_margin = "20%"
message_style = dict(
    padding_x="1em",
    padding_y="0.5em",
    border_radius="5px",
    margin_y="0.5em",
    box_shadow=shadow,
    max_width="50em",
    display="inline-block",
)

question_style = message_style | dict(
    margin_left=chat_margin,
    background_color=rx.color("gray", 7),
)
answer_style = message_style | dict(
    margin_right=chat_margin,
    background_color=rx.color("gray", 9),
)

input_style = dict(
    border_width="1px",
    padding="0.5em",
    box_shadow=shadow,
    width="47em",
    border="1px solid #222221",
    background_color=rx.color("mauve", 12),
)
button_style = dict(
    background_color=rx.color("sand", 5),
    box_shadow=shadow,
    color=rx.color("sand", 12),
)