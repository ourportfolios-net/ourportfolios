import reflex as rx

from ourportfolios.components.indices_grid import indices_grid
from ourportfolios.pages.home.components.refresh_countdown import refresh_countdown_ring
from ourportfolios.state.heatmap import (
    HeatmapChip,
    HeatmapState,
    HeatmapTile,
    TickerSubtile,
)
from ourportfolios.state.home_state import HomeState
from ourportfolios.state.prefs_state import PrefsState
from ourportfolios.ui.primitives import glass_box
from ourportfolios.ui.theme.colors import TEXT_PRIMARY, TEXT_TERTIARY, white
from ourportfolios.ui.theme.components import accent_button
from ourportfolios.ui.theme.surfaces import (
    CARD_BG,
    CARD_BORDER,
    RADIUS_2XS,
    RADIUS_4XS,
    RADIUS_BUTTON,
    RADIUS_INPUT,
    RADIUS_PILL,
    RADIUS_SURFACE,
    SKELETON_BG,
    TRANS_DEFAULT,
)
from ourportfolios.ui.tokens import TRANS_BG, TRANS_COLOR_FAST

_TREEMAP_H = "38.75rem"

_TILE_BG = "rgba(255, 255, 255, 0.03)"
_TILE_BORDER = "1px solid rgba(255, 255, 255, 0.07)"
_TILE_HOVER_BORDER = "rgba(255, 255, 255, 0.20)"
_SUBTILE_BORDER = "rgba(255, 255, 255, 0.05)"

_PERIOD_OPTIONS = ["1D", "1W", "1M", "1Q", "1Y"]


def _period_button(label: str) -> rx.Component:
    active = HeatmapState.selected_period == label
    return rx.box(
        rx.text(
            label,
            size="1",
            weight="medium",
            color=rx.cond(active, TEXT_PRIMARY, TEXT_TERTIARY),
        ),
        padding="0.18rem 0.5rem",
        border_radius=RADIUS_4XS,
        background=rx.cond(active, white(0.09), "transparent"),
        cursor="pointer",
        on_click=[
            HeatmapState.set_period(label),
            HomeState.load_ticker_for_period(label),
        ],
        _hover={"background": white(0.05)},
        transition=TRANS_BG,
    )


def _skel(w: str = "100%", h: str = "0.75rem", r: str = "0.375rem") -> rx.Component:
    """rx.skeleton — works fine for fixed sizes (used in indices col)."""
    return rx.skeleton(rx.box(width=w, height=h), loading=True, border_radius=r)


def _skel_box(w: str, h: str, r: str = "0.25rem") -> rx.Component:
    """Plain box skeleton — reliable with percentage widths (used in treemap area)."""
    return rx.box(width=w, height=h, border_radius=r, background=SKELETON_BG)


# ─── Indices skeleton ─────────────────────────────────────────────────────────


def _mini_index_card_skel() -> rx.Component:
    return rx.box(
        rx.hstack(
            rx.vstack(
                _skel("3rem", "0.5rem"),
                _skel("5.5rem", "1.5rem", "0.375rem"),
                _skel("3.5rem", "1rem", "0.5rem"),
                spacing="1",
                align="start",
                flex_shrink="0",
            ),
            rx.spacer(),
            _skel("5.625rem", "3.25rem", "0.375rem"),
            align="center",
            width="100%",
        ),
        padding="0.625rem 0.875rem",
        border_radius=RADIUS_INPUT,
        background=CARD_BG,
        border=CARD_BORDER,
        width="100%",
        box_sizing="border-box",
    )


def _indices_skeleton_vertical() -> rx.Component:
    return rx.vstack(
        _mini_index_card_skel(),
        _mini_index_card_skel(),
        _mini_index_card_skel(),
        _mini_index_card_skel(),
        spacing="3",
        width="100%",
    )


def _indices_skeleton_horizontal() -> rx.Component:
    return rx.box(
        rx.hstack(
            *[
                rx.box(_mini_index_card_skel(), min_width="11rem", flex_shrink="0")
                for _ in range(3)
            ],
            spacing="3",
            align="stretch",
            width="max-content",
        ),
        width="100%",
        overflow_x="auto",
        scrollbar_width="none",
        style={"&::-webkit-scrollbar": {"display": "none"}},
    )


# ─── Heatmap skeleton (plain boxes — no rx.skeleton, reliable at any width) ──


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


# ─── Desktop treemap ──────────────────────────────────────────────────────────


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
                t.pct_label,
                color_scheme=t.pct_color_scheme,
                variant="soft",
                size="1",
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
            border_radius=RADIUS_PILL,
            border=f"1px solid {_SUBTILE_BORDER}",
            transition="filter 0.12s ease",
            _hover={"filter": "brightness(1.22)"},
        ),
        href=t.url,
        position="absolute",
        left=f"calc({t.x}% + 2px)",
        top=f"calc({t.y}% + 2px)",
        width=f"calc({t.w}% - 4px)",
        height=f"calc({t.h}% - 4px)",
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
            border_radius=f"{RADIUS_SURFACE} {RADIUS_SURFACE} 0 0",
        ),
        rx.foreach(tile.tickers, _ticker_subtile),
        position="absolute",
        left=f"calc({tile.x}% + 4px)",
        top=f"calc({tile.y}%)",
        width=f"calc({tile.w}% - 8px)",
        height=f"calc({tile.h}% - 8px)",
        border_radius=RADIUS_SURFACE,
        border=_TILE_BORDER,
        background=tile.bg,
        overflow="hidden",
        cursor="pointer",
        transition=TRANS_DEFAULT,
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
        border_radius=RADIUS_PILL,
        background=_TILE_BG,
        border=_TILE_BORDER,
        flex_shrink="0",
        text_decoration="none",
        transition=TRANS_COLOR_FAST,
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


def _treemap() -> rx.Component:
    return rx.cond(
        HeatmapState.loading | (HeatmapState.tiles.length() == 0),
        _treemap_skeleton(),
        rx.vstack(
            rx.box(
                rx.foreach(HeatmapState.tiles, _industry_tile),
                position="relative",
                width="100%",
                height=_TREEMAP_H,
                border_radius=RADIUS_SURFACE,
                overflow="hidden",
            ),
            _chip_row(),
            spacing="0",
            width="100%",
        ),
    )


# ─── Mobile industry list ─────────────────────────────────────────────────────


def _mobile_tile_row(tile: HeatmapTile) -> rx.Component:
    return rx.link(
        rx.hstack(
            rx.text(
                tile.name,
                size="2",
                weight="bold",
                color=white(0.88),
                flex="1",
                overflow="hidden",
                text_overflow="ellipsis",
                white_space="nowrap",
                min_width="0",
            ),
            rx.badge(
                tile.pct_label,
                color_scheme=tile.pct_color_scheme,
                variant="soft",
                size="1",
                flex_shrink="0",
            ),
            spacing="3",
            align="center",
            width="100%",
            min_width="0",
        ),
        href=tile.url,
        text_decoration="none",
        display="flex",
        padding="0.6rem 0.75rem",
        border_radius=RADIUS_BUTTON,
        background=white(0.03),
        border=_TILE_BORDER,
        width="100%",
        transition=TRANS_BG,
        _hover={"border_color": _TILE_HOVER_BORDER, "background": white(0.05)},
    )


def _mobile_chip_row(c: HeatmapChip) -> rx.Component:
    return rx.link(
        rx.hstack(
            rx.text(
                c.name,
                size="2",
                weight="bold",
                color=white(0.78),
                flex="1",
                overflow="hidden",
                text_overflow="ellipsis",
                white_space="nowrap",
                min_width="0",
            ),
            rx.badge(
                c.pct_label,
                color_scheme=c.pct_color_scheme,
                variant="soft",
                size="1",
                flex_shrink="0",
            ),
            spacing="3",
            align="center",
            width="100%",
            min_width="0",
        ),
        href=c.url,
        text_decoration="none",
        display="flex",
        padding="0.6rem 0.75rem",
        border_radius=RADIUS_BUTTON,
        background=white(0.03),
        border=_TILE_BORDER,
        width="100%",
        transition=TRANS_BG,
        _hover={"border_color": _TILE_HOVER_BORDER, "background": white(0.05)},
    )


def _mobile_skeleton_row() -> rx.Component:
    return rx.box(
        rx.hstack(
            _skel("55%", "0.875rem"),
            rx.spacer(),
            _skel("3rem", "1.25rem", "0.5rem"),
            align="center",
            width="100%",
        ),
        padding="0.6rem 0.75rem",
        border_radius=RADIUS_BUTTON,
        background=white(0.03),
        border=_TILE_BORDER,
        width="100%",
    )


def _mobile_industry_view() -> rx.Component:
    return rx.cond(
        HeatmapState.loading | (HeatmapState.tiles.length() == 0),
        rx.vstack(
            *[_mobile_skeleton_row() for _ in range(8)],
            spacing="2",
            width="100%",
        ),
        rx.vstack(
            rx.foreach(HeatmapState.tiles, _mobile_tile_row),
            rx.vstack(
                rx.cond(
                    HeatmapState.chips,
                    rx.vstack(
                        rx.foreach(HeatmapState.chips, _mobile_chip_row),
                        spacing="2",
                        width="100%",
                    ),
                    rx.box(),
                ),
                spacing="2",
                width="100%",
            ),
            spacing="2",
            width="100%",
        ),
    )


# ─── Scrollable indices wrapper (mobile) ──────────────────────────────────────


# ─── Section assembly ─────────────────────────────────────────────────────────


def market_overview_section() -> rx.Component:
    return glass_box(
        rx.vstack(
            # ── Header ───────────────────────────────────────────────────
            rx.hstack(
                rx.hstack(
                    refresh_countdown_ring(),
                    rx.text(
                        "Market Overview",
                        size=rx.breakpoints(initial="2", md="3"),
                        weight="bold",
                        color=TEXT_PRIMARY,
                        letter_spacing="-0.01em",
                        white_space="nowrap",
                    ),
                    spacing="2",
                    align="center",
                    flex_shrink="1",
                    min_width="0",
                ),
                rx.spacer(),
                rx.hstack(
                    *[_period_button(p) for p in _PERIOD_OPTIONS],
                    spacing="0",
                    padding="0.16rem",
                    border_radius=RADIUS_2XS,
                    background=white(0.03),
                    border=f"1px solid {white(0.06)}",
                    flex_shrink="0",
                ),
                width="100%",
                align="center",
            ),
            # ── Content ───────────────────────────────────────────────────
            rx.flex(
                rx.vstack(
                    indices_grid(),
                    rx.box(
                        _mobile_industry_view(),
                        display=rx.breakpoints(initial="block", md="none"),
                        width="100%",
                    ),
                    width=rx.breakpoints(initial="100%", md="13.125rem"),
                    spacing="3",
                    flex_shrink="0",
                ),
                # Right Column (Treemap)
                rx.box(
                    _treemap(),
                    display=rx.breakpoints(initial="none", md="block"),
                    flex="1",
                    min_width="0",
                    width="100%",
                ),
                direction=rx.breakpoints(initial="column", md="row"),
                gap="0.75rem",
                width="100%",
                align="start",
                min_height=rx.breakpoints(initial="auto", md=_TREEMAP_H),
            ),
            accent_button("View Full Market", href="/market"),
            spacing="4",
            width="100%",
        ),
        padding=rx.breakpoints(initial="1rem", md="1.25rem 1.5rem"),
        width="100%",
        _hover={},
        on_mount=[PrefsState.apply_to_heatmap, HeatmapState.load_heatmap_data],
    )
