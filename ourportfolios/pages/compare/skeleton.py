"""Skeleton loading components for the comparison page."""

import reflex as rx


def skeleton_metric_cell() -> rx.Component:
    """Skeleton for a single metric cell in the comparison table."""
    return rx.hstack(
        # Value skeleton
        rx.skeleton(
            rx.box(height="1.2em", width="3em"),
        ),
        # Graph skeleton
        rx.skeleton(
            rx.box(height="56px", width="7em"),
        ),
        spacing="1",
        width="12em",
        min_width="12em",
        height="3.5em",
        align="center",
        border_right=f"1px solid {rx.color('gray', 4)}",
        padding_left="0.3em",
        padding_right="0.3em",
    )


def skeleton_stock_row(num_metrics: int = 7) -> rx.Component:
    """Skeleton for a single stock row in the comparison table."""
    return rx.card(
        rx.hstack(
            *[skeleton_metric_cell() for _ in range(num_metrics)],
            spacing="0",
            style={"flex_wrap": "nowrap"},
        ),
        height="3.5em",
        style={"flex_shrink": "0"},
    )


def skeleton_ticker_card() -> rx.Component:
    """Skeleton for a ticker card in the left column."""
    return rx.card(
        rx.vstack(
            rx.skeleton(
                rx.box(height="1.5em", width="4em"),
            ),
            rx.skeleton(
                rx.box(height="1em", width="6em"),
            ),
            rx.skeleton(
                rx.box(height="0.8em", width="5em"),
            ),
            spacing="2",
            justify="center",
            align="center",
        ),
        width="15em",
        height="3.5em",
        flex_shrink="0",
    )


def skeleton_table_section() -> rx.Component:
    """Skeleton for the entire comparison table."""
    return rx.hstack(
        # Fixed ticker symbols column on the left
        rx.box(
            rx.vstack(
                # Empty space for metric labels header
                rx.box(
                    height="3.5em",
                    width="15em",
                ),
                # Skeleton stock cards
                rx.vstack(
                    *[skeleton_ticker_card() for _ in range(3)],
                    spacing="2",
                ),
                spacing="0",
                width="15em",
            ),
            width="15em",
            flex_shrink="0",
        ),
        # Scrollable metrics area
        rx.scroll_area(
            rx.vstack(
                # Metric labels skeleton at the top
                rx.card(
                    rx.hstack(
                        *[
                            rx.skeleton(
                                rx.box(
                                    width="12em",
                                    min_width="12em",
                                    height="1.2em",
                                )
                            )
                            for _ in range(7)
                        ],
                        spacing="0",
                        height="100%",
                        align="center",
                        style={"flex_wrap": "nowrap"},
                    ),
                    height="3.5em",
                    style={"flex_shrink": "0"},
                ),
                # Skeleton stock rows
                *[skeleton_stock_row(7) for _ in range(3)],
                spacing="2",
                align="start",
            ),
            scrollbars="both",
            type="auto",
            style={
                "width": "100%",
                "max_height": "calc(100vh - 10em)",
            },
        ),
        spacing="5",
        align="start",
        width="100%",
        overflow="visible",
    )


def loading_comparison_skeleton() -> rx.Component:
    """Main skeleton component shown while data is loading."""
    return rx.box(
        rx.vstack(
            # Controls skeleton
            rx.hstack(
                rx.spacer(),
                rx.hstack(
                    rx.skeleton(rx.box(width="3em", height="2em")),
                    rx.skeleton(rx.box(width="3em", height="2em")),
                    rx.skeleton(rx.box(width="8em", height="2em")),
                    spacing="3",
                ),
                spacing="0",
                align="center",
                width="100%",
                margin_bottom="2em",
            ),
            # Table skeleton
            skeleton_table_section(),
            spacing="0",
            width="100%",
        ),
        width="100%",
        style={
            "max_width": "100vw",
            "margin": "0 auto",
            "padding_top": "1.5em",
            "padding_left": "1.5em",
            "padding_right": "1.5em",
        },
    )
