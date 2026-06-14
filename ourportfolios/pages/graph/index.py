"""Graph page entry point — routes to the knowledge graph visualization."""

import reflex as rx

from ourportfolios.components.navbar import navbar
from ourportfolios.ui.tokens import APP_BG

from .components import _all_scripts, main_content
from .state import GraphState


def _graph_layout(content: rx.Component) -> rx.Component:
    """Centered layout with graph filling remaining viewport height below navbar.

    Creates a flex chain: outer flexbox → center → frame → vstack → graph area.
    Each level has ``flex=1`` so the ``#cy-graph`` div gets a computed height.
    """
    return rx.box(
        navbar(),
        rx.center(
            rx.box(
                rx.vstack(
                    content,
                    spacing="4",
                    width="100%",
                    flex="1",
                    min_height="0",
                ),
                width=rx.breakpoints(initial="100%", lg="86vw"),
                max_width="90rem",
                padding_x=rx.breakpoints(initial="1rem", lg="0"),
                padding_y="1.8em",
                flex="1",
                display="flex",
                flex_direction="column",
                min_height="0",
            ),
            width="100%",
            flex="1",
            display="flex",
            flex_direction="column",
            min_height="0",
        ),
        background=APP_BG,
        color="white",
        min_height="100vh",
        width="100%",
        overflow_x="hidden",
        display="flex",
        flex_direction="column",
    )


@rx.page(
    route="/graph",
    on_load=GraphState.on_mount,
)
def index() -> rx.Component:
    """Knowledge graph page with interactive Cytoscape.js visualization."""
    return rx.box(
        _all_scripts(),
        _graph_layout(main_content()),
        width="100%",
    )
