import reflex as rx

from ...state.home_state import HomeState
from ...state.heatmap import HeatmapState, HeatmapTile, HeatmapChip, TickerSubtile
from ...components.cards import glass_card
from ...styles import (
    white,
    purple,
    black,
    CARD_BG,
    CARD_BORDER,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    TEXT_TERTIARY,
    accent_btn,
)

# Must match _CTR_W / _CTR_H in heatmap.py
_TREEMAP_W_PX = "760px"
_TREEMAP_H = "540px"


# ── Period button ───────────────────────────────────────────────────────────────


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
        border_radius="5px",
        background=rx.cond(active, white(0.09), "transparent"),
        cursor="pointer",
        on_click=HeatmapState.set_period(label),
        _hover={"background": white(0.05)},
        transition="background 0.12s ease",
    )


# ── VNIndex card ────────────────────────────────────────────────────────────────
# Compact: label → value + badge → sparkline, all in a single column.
# Fixed width so the treemap gets the rest of the hstack.


def _vnindex_card() -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.text("VNIndex", size="1", weight="medium", color=TEXT_TERTIARY),
            rx.hstack(
                rx.text(
                    HomeState.vnindex_value,
                    size="6",
                    weight="bold",
                    color=TEXT_PRIMARY,
                ),
                rx.badge(
                    HomeState.vnindex_change,
                    color_scheme=rx.cond(HomeState.vnindex_is_positive, "green", "red"),
                    variant="soft",
                    size="1",
                ),
                spacing="2",
                align="end",
            ),
            rx.box(flex="1"),
            rx.cond(
                HomeState.vnindex_chart_data,
                rx.recharts.area_chart(
                    rx.recharts.area(
                        data_key="normalized_close",
                        stroke=purple(0.80),
                        fill=purple(0.08),
                        stroke_width=1.5,
                        dot=False,
                        is_animation_active=False,
                    ),
                    rx.recharts.x_axis(data_key="name", hide=True),
                    rx.recharts.y_axis(domain=[0, 1], hide=True),
                    data=HomeState.vnindex_chart_data,
                    width=200,
                    height=80,
                    margin={"top": 4, "right": 0, "bottom": 0, "left": 0},
                ),
                rx.box(height="80px"),
            ),
            spacing="2",
            align="start",
            height="100%",
        ),
        padding="1rem",
        border_radius="10px",
        background=CARD_BG,
        border=CARD_BORDER,
        flex_shrink="0",
        width="220px",
        height=_TREEMAP_H,
        box_sizing="border-box",
    )


# ── Ticker subtile ──────────────────────────────────────────────────────────────
#
# CLICK FIX: The parent industry tile has NO on_click handler.
# Only the ticker rx.link and the industry label rx.link handle clicks.
# This prevents the "clicking ticker redirects to industry" bug.
#
# The ticker is an rx.link wrapping an rx.box. The <a> tag navigates to
# t.url (/tickers/...) and since there's no parent on_click, nothing else fires.


def _ticker_content(t: TickerSubtile) -> rx.Component:
    return rx.cond(
        t.size == "xl",
        rx.vstack(
            rx.text(
                t.symbol,
                size="5",
                weight="bold",
                color=TEXT_PRIMARY,
                text_align="center",
            ),
            rx.text(
                t.pct_label,
                size="2",
                weight="regular",
                color=t.pct_color,
                text_align="center",
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
                    color=TEXT_PRIMARY,
                    text_align="center",
                ),
                rx.text(
                    t.pct_label,
                    size="1",
                    weight="regular",
                    color=t.pct_color,
                    text_align="center",
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
                        color=TEXT_PRIMARY,
                        text_align="center",
                    ),
                    rx.text(
                        t.pct_label,
                        size="1",
                        weight="regular",
                        color=t.pct_color,
                        text_align="center",
                    ),
                    spacing="0",
                    align="center",
                ),
                rx.text(
                    t.symbol,
                    size="1",
                    weight="medium",
                    color=TEXT_SECONDARY,
                    text_align="center",
                ),
            ),
        ),
    )


def _ticker_subtile(t: TickerSubtile) -> rx.Component:
    """
    Absolutely-positioned ticker tile as an rx.link → /tickers/...
    No parent on_click exists, so click always goes to the ticker page.
    """
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
            border_radius="3px",
            transition="filter 0.08s ease",
            _hover={"filter": "brightness(1.20)"},
        ),
        href=t.url,
        position="absolute",
        left=f"calc({t.x}% + 1.5px)",
        top=f"calc({t.y}% + 1.5px)",
        width=f"calc({t.w}% - 3px)",
        height=f"calc({t.h}% - 3px)",
        z_index="2",
        text_decoration="none",
    )


# ── Industry label — links to /industries/... ───────────────────────────────────
# This is now an rx.link (not pointer-events:none).
# It lives in the top-left corner, above ticker subtiles.
# The label IS the clickable affordance for industry navigation.


def _ind_label(tile: HeatmapTile) -> rx.Component:
    return rx.link(
        rx.hstack(
            rx.text(
                tile.name,
                size="1",
                weight="medium",
                color=TEXT_SECONDARY,
                white_space="nowrap",
                overflow="hidden",
                text_overflow="ellipsis",
            ),
            rx.text(
                tile.pct_label,
                size="1",
                weight="regular",
                color=tile.pct_color,
                white_space="nowrap",
                flex_shrink="0",
            ),
            spacing="2",
            align="center",
            max_width="100%",
            overflow="hidden",
        ),
        href=tile.url,
        position="absolute",
        top="5px",
        left="6px",
        max_width="calc(100% - 12px)",
        overflow="hidden",
        z_index="10",
        background=black(0.62),
        padding="2px 7px 3px",
        border_radius="4px",
        backdrop_filter="blur(6px)",
        text_decoration="none",
        _hover={"background": black(0.80)},
        transition="background 0.10s ease",
    )


# ── Industry tile ───────────────────────────────────────────────────────────────
# NO on_click on the tile itself — click routing is handled exclusively by:
#   - _ind_label (rx.link → /industries/...)
#   - _ticker_subtile (rx.link → /tickers/...)
# The tile background uses tile.bg (muted industry colour, not black canvas).
# Hover brightens the tile background via filter on the tile box itself.
# Because subtiles have their own filter hover, the combined effect is fine.


def _industry_tile(tile: HeatmapTile) -> rx.Component:
    return rx.box(
        rx.foreach(tile.tickers, _ticker_subtile),
        _ind_label(tile),
        position="absolute",
        left=f"calc({tile.x}% + 3px)",
        top=f"calc({tile.y}% + 3px)",
        width=f"calc({tile.w}% - 6px)",
        height=f"calc({tile.h}% - 6px)",
        border_radius="8px",
        border=f"1px solid {tile.border}",
        # Muted coloured background — no black canvas
        background=tile.bg,
        overflow="hidden",
        cursor="default",
        # Tile-level brightness on hover so the industry stands out
        transition="filter 0.12s ease",
        _hover={"filter": "brightness(1.18)"},
    )


# ── Chip row ─────────────────────────────────────────────────────────────────────


def _chip(c: HeatmapChip) -> rx.Component:
    return rx.link(
        rx.hstack(
            rx.text(
                c.name,
                size="1",
                weight="medium",
                color=TEXT_SECONDARY,
                white_space="nowrap",
            ),
            rx.text(
                c.pct_label,
                size="1",
                weight="regular",
                color=c.pct_color,
                white_space="nowrap",
            ),
            spacing="2",
            align="center",
        ),
        href=c.url,
        padding="0.22rem 0.6rem",
        border_radius="6px",
        background=c.bg,
        border=f"1px solid {c.border}",
        flex_shrink="0",
        text_decoration="none",
        transition="filter 0.10s ease",
        _hover={"filter": "brightness(1.16)"},
        display="inline-flex",
    )


def _chip_row() -> rx.Component:
    return rx.cond(
        HeatmapState.chips,
        rx.box(
            rx.hstack(
                rx.foreach(HeatmapState.chips, _chip),
                spacing="2",
                wrap="wrap",
            ),
            padding_top="0.5rem",
            width="100%",
        ),
        rx.box(),
    )


# ── Treemap canvas ──────────────────────────────────────────────────────────────
# No background on the outer container — tiles float on the card surface.


def _treemap() -> rx.Component:
    return rx.cond(
        HeatmapState.loading,
        rx.center(rx.spinner(size="3"), width="100%", height=_TREEMAP_H),
        rx.cond(
            HeatmapState.tiles,
            rx.vstack(
                rx.box(
                    rx.foreach(HeatmapState.tiles, _industry_tile),
                    position="relative",
                    width="100%",
                    height=_TREEMAP_H,
                    border_radius="10px",
                    overflow="hidden",
                    # No background — the glass_card surface shows through the gaps
                ),
                _chip_row(),
                spacing="0",
                width="100%",
            ),
            rx.center(
                rx.text("No market data", size="2", color=TEXT_TERTIARY),
                width="100%",
                height=_TREEMAP_H,
            ),
        ),
    )


# ── Full section ────────────────────────────────────────────────────────────────


def market_overview_section() -> rx.Component:
    return glass_card(
        rx.vstack(
            # ── Header row ────────────────────────────────────────────────────
            rx.hstack(
                rx.hstack(
                    rx.box(
                        width="5px",
                        height="5px",
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
                    _period_btn("1D"),
                    _period_btn("1W"),
                    _period_btn("1M"),
                    _period_btn("1Y"),
                    spacing="0",
                    padding="0.16rem",
                    border_radius="7px",
                    background=white(0.03),
                    border=f"1px solid {white(0.06)}",
                ),
                width="100%",
                align="center",
            ),
            # ── VNIndex LEFT  |  Treemap RIGHT ────────────────────────────────
            rx.hstack(
                _vnindex_card(),
                rx.box(_treemap(), flex="1", min_width="0"),
                spacing="3",
                width="100%",
                align="start",
            ),
            accent_btn("View Full Market", href="/market"),
            spacing="4",
            width="100%",
        ),
        padding="1.25rem 1.5rem",
        width="100%",
        on_mount=HeatmapState.load_heatmap_data,
    )
