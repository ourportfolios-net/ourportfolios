import reflex as rx

from ...state.home_state import HomeState
from ...state.heatmap import HeatmapState, HeatmapTile, HeatmapChip, TickerSubtile
from ...state.prefs_state import PrefsState
from ...components.cards import glass_card
from ...styles import (
    white,
    purple,
    CARD_BG,
    CARD_BORDER,
    TEXT_PRIMARY,
    TEXT_TERTIARY,
    accent_btn,
)

_TREEMAP_H = "38.75rem"

_TILE_BG = "rgba(255, 255, 255, 0.03)"
_TILE_BORDER = "1px solid rgba(255, 255, 255, 0.07)"
_TILE_HOVER_BORDER = "rgba(255, 255, 255, 0.20)"
_SUBTILE_BORDER = "rgba(255, 255, 255, 0.05)"

# Only the 3 supported periods
_PERIOD_OPTIONS = ["1D", "1W", "1M"]


def _period_btn(label: str) -> rx.Component:
    active = HeatmapState.selected_period == label
    return rx.box(
        rx.text(
            label,
            size="1",
            weight="medium",
            color=rx.cond(active, TEXT_PRIMARY, TEXT_TERTIARY),
        ),
        padding="0.18rem 0.5rem",
        border_radius="0.3125rem",
        background=rx.cond(active, white(0.09), "transparent"),
        cursor="pointer",
        on_click=HeatmapState.set_period(label),
        _hover={"background": white(0.05)},
        transition="background 0.12s ease",
    )


def _skel(w: str = "100%", h: str = "0.75rem", r: str = "0.375rem") -> rx.Component:
    return rx.skeleton(rx.box(width=w, height=h), loading=True, border_radius=r)


def vnindex_card() -> rx.Component:
    _shell = dict(
        padding="0.875rem 1rem",
        border_radius="0.625rem",
        background=CARD_BG,
        border=CARD_BORDER,
        width="100%",
        box_sizing="border-box",
    )
    return rx.cond(
        HomeState.vnindex_value,
        rx.box(
            rx.vstack(
                rx.text("VNIndex", size="1", weight="medium", color=TEXT_TERTIARY),
                rx.hstack(
                    rx.vstack(
                        rx.text(
                            HomeState.vnindex_value,
                            size="6",
                            weight="bold",
                            color=TEXT_PRIMARY,
                            letter_spacing="-0.02em",
                            line_height="1",
                        ),
                        rx.badge(
                            HomeState.vnindex_change,
                            color_scheme=rx.cond(
                                HomeState.vnindex_is_positive, "green", "red"
                            ),
                            variant="soft",
                            size="1",
                        ),
                        spacing="2",
                        align="start",
                        flex_shrink="0",
                    ),
                    rx.recharts.area_chart(
                        rx.recharts.area(
                            data_key="normalized_close",
                            stroke=purple(0.85),
                            fill=purple(0.12),
                            stroke_width=1.8,
                            dot=False,
                            active_dot={"r": 4, "fill": purple(1.0), "strokeWidth": 0},
                            is_animation_active=False,
                        ),
                        rx.recharts.x_axis(data_key="name", hide=True),
                        rx.recharts.y_axis(domain=[0, 1], hide=True),
                        data=HomeState.vnindex_chart_data,
                        width=140,
                        height=70,
                        margin={"top": 8, "right": 8, "bottom": 8, "left": 4},
                    ),
                    spacing="3",
                    align="center",
                    width="100%",
                    flex="1",
                ),
                spacing="2",
                align="start",
                width="100%",
                height="100%",
            ),
            **_shell,
        ),
        rx.box(
            rx.vstack(
                _skel("3.25rem", "0.625rem"),
                rx.hstack(
                    rx.vstack(
                        _skel("5.5rem", "1.75rem", "0.375rem"),
                        _skel("3.5rem", "1.125rem", "0.5rem"),
                        spacing="2",
                    ),
                    _skel("8.75rem", "4.375rem", "0.375rem"),
                    spacing="3",
                    align="center",
                    width="100%",
                ),
                spacing="2",
                align="start",
                width="100%",
            ),
            **_shell,
        ),
    )


def _ticker_content(t: TickerSubtile) -> rx.Component:
    return rx.cond(
        t.size == "xl",
        rx.vstack(
            rx.text(
                t.symbol,
                size="5",
                weight="bold",
                color=white(0.95),
                text_align="center",
            ),
            rx.badge(
                t.pct_label, color_scheme=t.pct_color_scheme, variant="soft", size="1"
            ),
            spacing="1",
            align="center",
        ),
        rx.cond(
            t.size == "large",
            rx.vstack(
                rx.text(
                    t.symbol,
                    size="3",
                    weight="bold",
                    color=white(0.92),
                    text_align="center",
                ),
                rx.badge(
                    t.pct_label,
                    color_scheme=t.pct_color_scheme,
                    variant="soft",
                    size="1",
                ),
                spacing="1",
                align="center",
            ),
            rx.cond(
                t.size == "medium",
                rx.vstack(
                    rx.text(
                        t.symbol,
                        size="2",
                        weight="medium",
                        color=white(0.88),
                        text_align="center",
                    ),
                    rx.badge(
                        t.pct_label,
                        color_scheme=t.pct_color_scheme,
                        variant="soft",
                        size="1",
                    ),
                    spacing="0",
                    align="center",
                ),
                rx.vstack(
                    rx.text(
                        t.symbol,
                        size="1",
                        weight="medium",
                        color=white(0.80),
                        text_align="center",
                    ),
                    rx.badge(
                        t.pct_label,
                        color_scheme=t.pct_color_scheme,
                        variant="soft",
                        size="1",
                    ),
                    spacing="0",
                    align="center",
                ),
            ),
        ),
    )


def _ticker_subtile(t: TickerSubtile) -> rx.Component:
    return rx.link(
        rx.box(
            _ticker_content(t),
            width="100%",
            height="100%",
            display="flex",
            align_items="center",
            justify_content="center",
            overflow="hidden",
            background=t.bg,
            border_radius="0.375rem",
            border=f"1px solid {_SUBTILE_BORDER}",
            transition="filter 0.12s ease",
            _hover={"filter": "brightness(1.22)"},
        ),
        href=t.url,
        position="absolute",
        left=f"calc({t.x}% + 3px)",
        top=f"calc({t.y}% + 3px)",
        width=f"calc({t.w}% - 6px)",
        height=f"calc({t.h}% - 6px)",
        z_index="2",
        text_decoration="none",
    )


def _industry_tile(tile: HeatmapTile) -> rx.Component:
    return rx.box(
        rx.link(
            rx.hstack(
                rx.text(
                    tile.name,
                    size="1",
                    weight="bold",
                    color=white(0.85),
                    white_space="nowrap",
                    overflow="hidden",
                    text_overflow="ellipsis",
                ),
                rx.badge(
                    tile.pct_label,
                    color_scheme=tile.pct_color_scheme,
                    variant="soft",
                    size="1",
                    flex_shrink="0",
                ),
                spacing="2",
                align="center",
                overflow="hidden",
                max_width="100%",
            ),
            href=tile.url,
            text_decoration="none",
            position="absolute",
            top="0",
            left="0",
            right="0",
            height="1.875rem",
            display="flex",
            align_items="center",
            padding="0 0.625rem",
            z_index="10",
            border_bottom=f"1px solid {_SUBTILE_BORDER}",
            border_radius="0.75rem 0.75rem 0 0",
        ),
        rx.foreach(tile.tickers, _ticker_subtile),
        position="absolute",
        left=f"calc({tile.x}% + 4px)",
        top=f"calc({tile.y}% + 4px)",
        width=f"calc({tile.w}% - 8px)",
        height=f"calc({tile.h}% - 8px)",
        border_radius="0.75rem",
        border=_TILE_BORDER,
        background=tile.bg,
        overflow="hidden",
        cursor="pointer",
        transition="border-color 0.15s ease, box-shadow 0.15s ease",
        _hover={
            "border_color": _TILE_HOVER_BORDER,
            "box_shadow": f"inset 0 0 0 1px {white(0.10)}, 0 4px 20px rgba(0,0,0,0.28)",
        },
    )


def _chip(c: HeatmapChip) -> rx.Component:
    return rx.link(
        rx.hstack(
            rx.text(
                c.name,
                size="1",
                weight="medium",
                color=white(0.55),
                white_space="nowrap",
            ),
            rx.badge(
                c.pct_label,
                color_scheme=c.pct_color_scheme,
                variant="soft",
                size="1",
                flex_shrink="0",
            ),
            spacing="2",
            align="center",
        ),
        href=c.url,
        padding="0.2rem 0.6rem",
        border_radius="0.375rem",
        background=_TILE_BG,
        border=_TILE_BORDER,
        flex_shrink="0",
        text_decoration="none",
        transition="border-color 0.12s ease",
        _hover={"border_color": _TILE_HOVER_BORDER},
        display="inline-flex",
    )


def _chip_row() -> rx.Component:
    return rx.cond(
        HeatmapState.chips,
        rx.box(
            rx.hstack(rx.foreach(HeatmapState.chips, _chip), spacing="2", wrap="wrap"),
            padding_top="0.625rem",
            width="100%",
        ),
        rx.box(),
    )


def _treemap_skeleton() -> rx.Component:
    return rx.vstack(
        rx.hstack(
            _skel("42%", "12.5rem", "0.5rem"),
            _skel("35%", "12.5rem", "0.5rem"),
            _skel("23%", "12.5rem", "0.5rem"),
            spacing="2",
            width="100%",
        ),
        rx.hstack(
            _skel("33%", "11.875rem", "0.5rem"),
            _skel("33%", "11.875rem", "0.5rem"),
            _skel("33%", "11.875rem", "0.5rem"),
            spacing="2",
            width="100%",
        ),
        rx.hstack(
            _skel("25%", "11.25rem", "0.5rem"),
            _skel("38%", "11.25rem", "0.5rem"),
            _skel("37%", "11.25rem", "0.5rem"),
            spacing="2",
            width="100%",
        ),
        spacing="2",
        width="100%",
        height=_TREEMAP_H,
        overflow="hidden",
    )


def _treemap() -> rx.Component:
    return rx.cond(
        HeatmapState.tiles,
        rx.vstack(
            rx.box(
                rx.foreach(HeatmapState.tiles, _industry_tile),
                position="relative",
                width="100%",
                height=_TREEMAP_H,
                border_radius="0.75rem",
                overflow="hidden",
            ),
            _chip_row(),
            spacing="0",
            width="100%",
        ),
        _treemap_skeleton(),
    )


def market_overview_section() -> rx.Component:
    return glass_card(
        rx.vstack(
            rx.hstack(
                rx.hstack(
                    rx.box(
                        width="0.3125rem",
                        height="0.3125rem",
                        border_radius="50%",
                        background=purple(0.85),
                    ),
                    rx.text(
                        "MARKET OVERVIEW",
                        size="1",
                        weight="medium",
                        color=TEXT_TERTIARY,
                        letter_spacing="0.09em",
                    ),
                    spacing="2",
                    align="center",
                ),
                rx.spacer(),
                rx.hstack(
                    *[_period_btn(p) for p in _PERIOD_OPTIONS],
                    spacing="0",
                    padding="0.16rem",
                    border_radius="0.4375rem",
                    background=white(0.03),
                    border=f"1px solid {white(0.06)}",
                ),
                width="100%",
                align="center",
            ),
            rx.flex(
                rx.vstack(
                    vnindex_card(),
                    spacing="3",
                    width=rx.breakpoints(initial="100%", md="13.125rem"),
                    flex_shrink="0",
                    align="start",
                ),
                rx.box(_treemap(), flex="1", min_width="0"),
                direction=rx.breakpoints(initial="column", md="row"),
                gap="0.75rem",
                width="100%",
                align="start",
            ),
            accent_btn("View Full Market", href="/market"),
            spacing="4",
            width="100%",
        ),
        padding="1.25rem 1.5rem",
        width="100%",
        _hover={},
        # Load prefs first so selected_period is set before heatmap data arrives
        on_mount=[PrefsState.apply_to_heatmap, HeatmapState.load_heatmap_data],
    )
