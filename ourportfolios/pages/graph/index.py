"""Graph page entry point — routes to the knowledge graph visualization."""

import reflex as rx

from ourportfolios.components.navbar import navbar
from ourportfolios.ui.layout import app_shell, page_frame

from .components import _all_scripts, main_content
from .state import GraphState


def _graph_layout(content: rx.Component) -> rx.Component:
    """Uses the common layout shell but preserves graph's specific width."""
    return app_shell(
        navbar(),
        rx.center(
            page_frame(
                rx.vstack(
                    content,
                    spacing="4",
                    width="100%",
                ),
                width=rx.breakpoints(initial="100%", lg="86vw"),
                max_width="90rem",
                padding_x=rx.breakpoints(initial="1rem", lg="0"),
                padding_y="1.8em",  # Matches the old padding_bottom
            ),
            width="100%",
            position="relative",
        ),
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
        on_unmount=GraphState.on_unmount,
        width="100%",
    )
