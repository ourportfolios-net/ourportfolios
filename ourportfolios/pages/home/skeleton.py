"""
Skeleton loading components for the homepage.
Each skeleton mirrors the real component's layout so there's no layout shift on load.
All use a pulsing shimmer animation over the glass card surface.
"""

import reflex as rx
from ...styles import white, CARD_BG, CARD_BORDER, TEXT_TERTIARY


# ── Shimmer base ───────────────────────────────────────────────────────────────
# A single reusable shimmer block. Width/height/border_radius passed by caller.

_SHIMMER_BG = (
    "linear-gradient("
    "90deg,"
    "rgba(255,255,255,0.04) 0%,"
    "rgba(255,255,255,0.09) 50%,"
    "rgba(255,255,255,0.04) 100%"
    ")"
)
_SHIMMER_KEYFRAMES = "@keyframes shimmer { 0%{background-position:-400px 0} 100%{background-position:400px 0} }"


def _shimmer(
    width: str = "100%",
    height: str = "12px",
    border_radius: str = "5px",
    **kwargs,
) -> rx.Component:
    return rx.box(
        width=width,
        height=height,
        border_radius=border_radius,
        background=_SHIMMER_BG,
        background_size="800px 100%",
        animation="shimmer 1.6s infinite linear",
        style={
            "@keyframes shimmer": {
                "0%": {"backgroundPosition": "-400px 0"},
                "100%": {"backgroundPosition": "400px 0"},
            }
        },
        **kwargs,
    )


def _glass_shell(
    *children, padding: str = "1rem 1.125rem", height: str = "auto", **kwargs
) -> rx.Component:
    """Glass card shaped outer shell for a skeleton."""
    return rx.box(
        *children,
        padding=padding,
        border_radius="14px",
        background=CARD_BG,
        border=CARD_BORDER,
        width="100%",
        height=height,
        box_sizing="border-box",
        overflow="hidden",
        **kwargs,
    )


# ── VNIndex card skeleton ──────────────────────────────────────────────────────


def vnindex_card_skeleton() -> rx.Component:
    return rx.box(
        rx.vstack(
            _shimmer(width="52px", height="10px"),  # "VNIndex" label
            rx.hstack(
                rx.vstack(
                    _shimmer(width="88px", height="28px", border_radius="6px"),  # value
                    _shimmer(width="56px", height="18px", border_radius="8px"),  # badge
                    spacing="2",
                ),
                _shimmer(width="140px", height="70px", border_radius="6px"),  # chart
                spacing="3",
                align="center",
                width="100%",
            ),
            spacing="2",
            align="start",
            width="100%",
        ),
        padding="0.875rem 1rem",
        border_radius="10px",
        background=CARD_BG,
        border=CARD_BORDER,
        width="100%",
        box_sizing="border-box",
    )


# ── Ticker of the Day skeleton ─────────────────────────────────────────────────


def ticker_of_day_skeleton() -> rx.Component:
    return _glass_shell(
        rx.vstack(
            _shimmer(width="90px", height="10px"),  # "Ticker of the Day"
            rx.hstack(
                rx.hstack(
                    _shimmer(
                        width="80px", height="40px", border_radius="6px"
                    ),  # symbol
                    _shimmer(
                        width="32px", height="32px", border_radius="7px"
                    ),  # cart btn
                    spacing="2",
                    align="center",
                ),
                rx.spacer(),
                rx.vstack(
                    _shimmer(width="72px", height="24px", border_radius="6px"),  # price
                    _shimmer(width="52px", height="18px", border_radius="8px"),  # badge
                    spacing="1",
                    align="end",
                ),
                width="100%",
                align="center",
            ),
            _shimmer(width="120px", height="10px"),  # company name
            spacing="1",
            width="100%",
        ),
        padding="1rem 1.125rem",
    )


# ── Market heatmap skeleton ────────────────────────────────────────────────────
# Mirrors the glass_card wrapper + header row + 620px treemap area


def _heatmap_tile_skeleton(w: str, h: str) -> rx.Component:
    return rx.box(
        _shimmer(width="100%", height="100%", border_radius="8px"),
        width=w,
        height=h,
        border_radius="8px",
        overflow="hidden",
        flex_shrink="0",
    )


def market_overview_skeleton() -> rx.Component:
    return _glass_shell(
        rx.vstack(
            # Header
            rx.hstack(
                rx.hstack(
                    _shimmer(width="5px", height="5px", border_radius="50%"),
                    _shimmer(width="110px", height="10px"),
                    spacing="2",
                    align="center",
                ),
                rx.spacer(),
                _shimmer(
                    width="120px", height="24px", border_radius="7px"
                ),  # period toggles
                width="100%",
                align="center",
            ),
            # Body: left index cards + right treemap
            rx.hstack(
                # Left column
                rx.vstack(
                    vnindex_card_skeleton(),
                    spacing="3",
                    width="210px",
                    flex_shrink="0",
                ),
                # Right: treemap grid — 3×3 approximate tile layout
                rx.box(
                    rx.vstack(
                        rx.hstack(
                            _heatmap_tile_skeleton("42%", "200px"),
                            _heatmap_tile_skeleton("35%", "200px"),
                            _heatmap_tile_skeleton("23%", "200px"),
                            spacing="2",
                            width="100%",
                        ),
                        rx.hstack(
                            _heatmap_tile_skeleton("33%", "190px"),
                            _heatmap_tile_skeleton("33%", "190px"),
                            _heatmap_tile_skeleton("33%", "190px"),
                            spacing="2",
                            width="100%",
                        ),
                        rx.hstack(
                            _heatmap_tile_skeleton("25%", "180px"),
                            _heatmap_tile_skeleton("38%", "180px"),
                            _heatmap_tile_skeleton("37%", "180px"),
                            spacing="2",
                            width="100%",
                        ),
                        spacing="2",
                        width="100%",
                    ),
                    flex="1",
                    min_width="0",
                    height="620px",
                    overflow="hidden",
                ),
                spacing="3",
                width="100%",
                align="start",
            ),
            # CTA button placeholder
            _shimmer(width="140px", height="32px", border_radius="7px"),
            spacing="4",
            width="100%",
        ),
        padding="1.25rem 1.5rem",
        height="auto",
    )


# ── Decision hub skeleton (3-col grid of cards) ────────────────────────────────


def _hub_card_skeleton() -> rx.Component:
    return _glass_shell(
        rx.vstack(
            _shimmer(width="60%", height="10px"),
            _shimmer(width="100%", height="60px", border_radius="8px"),
            _shimmer(width="80px", height="28px", border_radius="7px"),
            spacing="3",
            width="100%",
        ),
        padding="1rem 1.125rem",
        height="140px",
    )


def decision_hub_skeleton() -> rx.Component:
    return rx.grid(
        _hub_card_skeleton(),
        _hub_card_skeleton(),
        _hub_card_skeleton(),
        columns=rx.breakpoints(initial="1", md="3", lg="3"),
        gap="1.25rem",
        width="100%",
    )


# ── Framework card skeleton ────────────────────────────────────────────────────


def framework_card_skeleton() -> rx.Component:
    return _glass_shell(
        rx.vstack(
            _shimmer(width="70px", height="10px"),
            _shimmer(width="100%", height="44px", border_radius="8px"),
            _shimmer(width="100%", height="44px", border_radius="8px"),
            _shimmer(width="100%", height="44px", border_radius="8px"),
            spacing="3",
            width="100%",
        ),
        padding="1rem 1.125rem",
    )


# ── Cart card skeleton ─────────────────────────────────────────────────────────


def cart_card_skeleton() -> rx.Component:
    return _glass_shell(
        rx.vstack(
            rx.hstack(
                _shimmer(width="40px", height="10px"),
                rx.spacer(),
                _shimmer(width="24px", height="24px", border_radius="6px"),
                width="100%",
                align="center",
            ),
            _shimmer(width="100%", height="40px", border_radius="8px"),
            _shimmer(width="100%", height="40px", border_radius="8px"),
            _shimmer(width="80px", height="28px", border_radius="7px"),
            spacing="3",
            width="100%",
        ),
        padding="1rem 1.125rem",
    )


# ── Full homepage skeleton ─────────────────────────────────────────────────────
# Drop-in replacement for the real page body while HomeState.loading is True.


def homepage_skeleton() -> rx.Component:
    return rx.flex(
        # Left column — 75%
        rx.box(
            rx.vstack(
                market_overview_skeleton(),
                decision_hub_skeleton(),
                spacing="5",
                width="100%",
            ),
            width=rx.breakpoints(initial="100%", lg="75%"),
        ),
        # Right column — 25%
        rx.box(
            rx.vstack(
                ticker_of_day_skeleton(),
                framework_card_skeleton(),
                cart_card_skeleton(),
                spacing="5",
                width="100%",
            ),
            width=rx.breakpoints(initial="100%", lg="25%"),
            margin_top=rx.breakpoints(initial="1.5rem", lg="0"),
        ),
        direction=rx.breakpoints(initial="column", lg="row"),
        gap=rx.breakpoints(initial="0", lg="2rem"),
        width="100%",
    )
