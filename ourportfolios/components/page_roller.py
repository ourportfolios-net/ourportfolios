import reflex as rx
from .cards import card_wrapper


def card_link(content, href):
    return rx.link(
        content,
        href=href,
        color="inherit",
        text_decoration="none",
        width="100%",
        transition="color 0.2s",
        cursor="pointer",
        class_name="card-link",
    )


# Shared props for side cards
_SIDE_CARD = dict(
    backdrop_filter="blur(14px)",
    z_index="1",
    box_shadow="0 4px 24px rgba(0,0,0,0.10)",
    position="absolute",
    top="50%",
    transform="translateY(-50%)",
    transition="transform 0.2s, box-shadow 0.2s, z-index 0.2s",
    width="13.8em",
    height="6.5em",
    display="flex",
    align_items="center",
    justify_content="center",
    padding="1em",
)

# Shared props for center card
_MAIN_CARD = dict(
    backdrop_filter="blur(14px)",
    z_index="2",
    position="relative",
    width="17.8em",
    height="7.8em",
    transition="transform 0.2s, box-shadow 0.2s, z-index 0.2s",
    align_items="center",
    justify_content="center",
    _hover={"transform": "scale(1.03)"},
    padding="2em 2.5em",
)


def card_roller(left_content, center_content, right_content):
    left = rx.box(
        card_wrapper(left_content, **_SIDE_CARD, left="-2.5em"),
        _hover={"transform": "translateX(-0.6em) scale(1.03)"},
        transition="transform 0.2s, z-index 0.2s",
        position="absolute",
        left="-1.5em",
        top="0",
        height="100%",
        width="16em",
        pointer_events="auto",
    )
    right = rx.box(
        card_wrapper(right_content, **_SIDE_CARD, right="-2.5em"),
        _hover={"transform": "translateX(0.6em) scale(1.03)"},
        transition="transform 0.2s, z-index 0.2s",
        position="absolute",
        right="-1.5em",
        top="0",
        height="100%",
        width="16em",
        pointer_events="auto",
    )
    center = card_wrapper(center_content, **_MAIN_CARD)
    return rx.box(
        left,
        right,
        center,
        position="relative",
        width="34em",
        height="10em",
        display="flex",
        align_items="center",
        justify_content="center",
    )
