"""Comparison and portfolio cards for the Home dashboard."""

from __future__ import annotations

import reflex as rx

from ourportfolios.pages.home.components.card_shell import (
    CARD_HEADER_HEIGHT,
    CARD_PREVIEW_SURFACE_HEIGHT,
    HUB_CARD_STYLE,
    HUB_CARD_TEXT_CLAMP,
    skeleton,
)
from ourportfolios.state.framework_state import GlobalFrameworkState
from ourportfolios.state.home_state import HomeState
from ourportfolios.ui.primitives import glass_box
from ourportfolios.ui.theme.colors import TEXT_TERTIARY, blue, green, white
from ourportfolios.ui.theme.components import accent_button
from ourportfolios.ui.theme.surfaces import PREVIEW_BOX_STYLE
from ourportfolios.ui.tokens import RADIUS_SM

_HUB_CSS = """
.hub-card { contain: layout style; }

.compare-bar-inner {
    transform: scaleX(0);
    transform-origin: left center;
    transition: transform 0.22s cubic-bezier(0.4, 0, 0.2, 1);
    will-change: transform;
}
.hub-card:hover .compare-bar-inner { transform: scaleX(1); }

.perf-bar-fill {
    transform: scaleX(0.4);
    opacity: 1;
    background: var(--base-color);
    transform-origin: left center;
    transition: transform 0.28s cubic-bezier(0.34, 1.56, 0.64, 1), background 0.28s ease;
    will-change: transform, background;
}
.hub-card:hover .perf-bar-fill {
    transform: scaleX(var(--bar-scale));
    background: var(--hover-color);
}
"""

_inject_hub_css = rx.script(
    f"""(function(){{var id='hub-css';if(!document.getElementById(id)){{var s=document.createElement('style');s.id=id;s.textContent={_HUB_CSS!r};document.head.appendChild(s);}}}})();""",
)


def _compare_col(color: str) -> rx.Component:
    return rx.box(
        rx.box(
            width="3.5rem",
            height="0.75rem",
            border_radius=RADIUS_SM,
            background=color,
            class_name="compare-bar-inner",
            # No style prop — transform/transition handled entirely by CSS class above
        ),
        width="3.5rem",
        flex_shrink="0",
        overflow="hidden",
    )


def _compare_row(col1: str, col2: str) -> rx.Component:
    return rx.hstack(
        rx.box(
            width="3.5rem",
            height="1.25rem",
            border_radius=RADIUS_SM,
            background=white(0.06),
        ),
        _compare_col(col1),
        _compare_col(col2),
        spacing="2",
        align="center",
        width="100%",
        padding="0.5rem 0.625rem",
        border_radius=RADIUS_SM,
        background=white(0.02),
        border=f"1px solid {white(0.04)}",
    )


def _comparison_preview() -> rx.Component:
    return rx.box(
        rx.vstack(
            skeleton("4.0625rem"),
            _compare_row(blue(0.45), white(0.08)),
            _compare_row(white(0.08), blue(0.45)),
            spacing="2",
            width="100%",
        ),
        style=PREVIEW_BOX_STYLE,
        height=CARD_PREVIEW_SURFACE_HEIGHT,
    )


def _perf_bar(hover_width: str, hover_color: str) -> rx.Component:
    scale = str(round(float(hover_width.rstrip("%")) / 100, 4))
    return rx.hstack(
        rx.box(
            width="1.875rem",
            height="0.6875rem",
            border_radius=RADIUS_SM,
            background=white(0.06),
        ),
        rx.box(
            rx.box(
                class_name="perf-bar-fill",
                width="100%",
                height="100%",
                border_radius=RADIUS_SM,
                # Only CSS variable set inline — safe, no specificity conflict
                style={
                    "--bar-scale": scale,
                    "--base-color": white(0.08),
                    "--hover-color": hover_color,
                },
            ),
            width="100%",
            height="0.6875rem",
            background=white(0.04),
            border_radius=RADIUS_SM,
            overflow="hidden",
            flex="1",
        ),
        spacing="3",
        align="center",
        width="100%",
    )


def _portfolio_preview() -> rx.Component:
    return rx.box(
        rx.vstack(
            skeleton("3.75rem"),
            skeleton("100%", height="1.875rem"),
            rx.vstack(
                _perf_bar("68%", green(0.5)),
                _perf_bar("42%", green(0.35)),
                _perf_bar("28%", green(0.25)),
                spacing="3",
                width="100%",
            ),
            spacing="3",
            width="100%",
        ),
        style=PREVIEW_BOX_STYLE,
        height=CARD_PREVIEW_SURFACE_HEIGHT,
    )


def _gradient_overlay(color: str) -> rx.Component:
    return rx.box(
        position="absolute",
        top="0",
        right="0",
        width="7rem",
        height="7rem",
        background=f"radial-gradient(ellipse at top right, {color}, transparent 60%)",
        border_radius=RADIUS_SM,
        pointer_events="none",
        z_index="1",
    )


def _hub_card(  # noqa: PLR0913
    title: str,
    description: str,
    gradient_color: str,
    preview: rx.Component,
    cta_label: str,
    on_click: object,
) -> rx.Component:
    return rx.box(
        _inject_hub_css,
        _gradient_overlay(gradient_color),
        rx.vstack(
            rx.hstack(
                rx.vstack(
                    rx.text(title, size="4", weight="bold", color="white"),
                    rx.text(
                        description,
                        size="2",
                        color=TEXT_TERTIARY,
                        line_height="1.65",
                        style={
                            "display": "-webkit-box",
                            "-webkit-line-clamp": "3",
                            "-webkit-box-orient": "vertical",
                            "overflow": "hidden",
                        },
                    ),
                    spacing="2",
                    align="start",
                    flex="1",
                    min_width="0",
                ),
                spacing="3",
                align="start",
                width="100%",
            ),
            preview,
            rx.spacer(),
            accent_button(cta_label, on_click=on_click),
            spacing="4",
            width="100%",
            height="100%",
        ),
        rx.box(
            position="absolute",
            top="0",
            left="0",
            width="100%",
            height="100%",
            z_index="0",
            cursor="pointer",
            on_click=on_click,
        ),
        style=HUB_CARD_STYLE,
        class_name="hub-card",
        # on_mouse_enter / on_mouse_leave removed — Python round-trips were the lag source
    )


def compare_assets_card() -> rx.Component:
    return _hub_card(
        title="Compare Assets",
        description="Head-to-head metrics. Analyze P/E, EPS, and Volatility side-by-side.",
        gradient_color="rgba(59, 130, 246, 0.10)",
        preview=_comparison_preview(),
        cta_label="Go to Comparison",
        on_click=HomeState.handle_compare,
    )


def manage_portfolio_card() -> rx.Component:
    return _hub_card(
        title="Manage Portfolio",
        description="Track performance, view allocation and rebalance your current holdings.",
        gradient_color="rgba(34, 197, 94, 0.08)",
        preview=_portfolio_preview(),
        cta_label="Open Portfolio",
        on_click=HomeState.handle_portfolio,
    )


_CARD_STACK_HEIGHT = "12.5rem"

_FW_CSS = f"""
.framework-card {{ contain: layout style; }}

.framework-card .fw-skel-0 {{
    opacity: 0;
    transition: opacity 0.22s ease;
}}
.framework-card .fw-skel-1 {{
    opacity: 1;
    transition: opacity 0.22s ease;
}}
.framework-card:hover .fw-skel-0 {{ opacity: 1; }}
.framework-card:hover .fw-skel-1 {{ opacity: 0; }}

.framework-card .fw-sliding-inner {{
    transform: translateY(0);
    transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    will-change: transform;
}}
.framework-card:hover .fw-sliding-inner {{
    transform: translateY(calc(-{CARD_HEADER_HEIGHT} - 0.5rem));
}}

.framework-card .fw-highlight {{
    transform: translateY(0);
    transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    will-change: transform;
}}
.framework-card:hover .fw-highlight {{
    transform: translateY(calc({CARD_HEADER_HEIGHT} + 0.5rem));
}}
"""

_inject_fw_css = rx.script(
    f"""(function(){{var id='fw-css';if(!document.getElementById(id)){{var s=document.createElement('style');s.id=id;s.textContent={_FW_CSS!r};document.head.appendChild(s);}}}})();""",
)


def _skeleton_row(icon_name: str, index: int) -> rx.Component:
    return rx.box(
        rx.hstack(
            rx.box(
                rx.icon(icon_name, size=15, color=white(0.2)),
                background=white(0.05),
                border=f"1px solid {white(0.06)}",
                border_radius=RADIUS_SM,
                padding="0.4375rem",
                display="flex",
                align_items="center",
                justify_content="center",
                flex_shrink="0",
            ),
            rx.vstack(
                skeleton("5.625rem", "0.75rem"),
                skeleton("100%", "1.25rem"),
                spacing="2",
                align="start",
                flex="1",
                min_width="0",
                overflow="hidden",
            ),
            spacing="3",
            align="center",
            width="100%",
        ),
        padding="0.625rem 0.75rem",
        border_radius=RADIUS_SM,
        background=white(0.02),
        border=f"1px solid {white(0.04)}",
        width="100%",
        height=CARD_HEADER_HEIGHT,
        class_name=f"fw-skel-{index}",
        # No opacity/transition inline — handled entirely by CSS class rules above
    )


def _glass_row(icon_name: str, title: str, description: str) -> rx.Component:
    return rx.hstack(
        rx.box(
            rx.icon(icon_name, size=15, color=white(0.55)),
            background=white(0.06),
            border=f"1px solid {white(0.08)}",
            border_radius=RADIUS_SM,
            padding="0.4375rem",
            display="flex",
            align_items="center",
            justify_content="center",
            flex_shrink="0",
        ),
        rx.vstack(
            rx.text(title, size="2", weight="bold", color="white"),
            rx.text(description, size="1", color=white(0.4), line_height="1.4"),
            spacing="0",
            align="start",
            flex="1",
            min_width="0",
            overflow="hidden",
        ),
        spacing="3",
        align="center",
        width="100%",
        height="100%",
        padding="0.625rem 0.75rem",
    )


def _framework_preview() -> rx.Component:
    return rx.box(
        rx.vstack(
            skeleton("3.75rem", RADIUS_SM),
            rx.box(
                rx.vstack(
                    _skeleton_row("shield", 0),
                    _skeleton_row("zap", 1),
                    spacing="2",
                    align="start",
                    width="100%",
                ),
                rx.box(
                    rx.box(
                        rx.box(
                            _glass_row(
                                "shield",
                                "Value Investing",
                                "Focuses on undervalued assets with strong fundamentals.",
                            ),
                            position="absolute",
                            top="0",
                            left="0",
                            right="0",
                            height=CARD_HEADER_HEIGHT,
                        ),
                        rx.box(
                            _glass_row(
                                "zap",
                                "Growth Strategy",
                                "Targets high-growth companies with expanding market share.",
                            ),
                            position="absolute",
                            top=f"calc({CARD_HEADER_HEIGHT} + 0.5rem)",
                            left="0",
                            right="0",
                            height=CARD_HEADER_HEIGHT,
                        ),
                        class_name="fw-sliding-inner",
                        position="absolute",
                        top="0",
                        left="0",
                        right="0",
                        height=f"calc({CARD_HEADER_HEIGHT} * 2 + 0.5rem)",
                        # No transform inline — CSS class handles it
                    ),
                    class_name="fw-highlight",
                    position="absolute",
                    top="0",
                    left="0",
                    right="0",
                    height=CARD_HEADER_HEIGHT,
                    background=white(0.05),
                    border_radius=RADIUS_SM,
                    border=f"1px solid {white(0.1)}",
                    overflow="hidden",
                    pointer_events="none",
                    # No transform inline — CSS class handles it
                ),
                position="relative",
                width="100%",
                height=f"calc({CARD_HEADER_HEIGHT} * 2 + 0.5rem)",
            ),
            spacing="2",
            align="start",
            width="100%",
        ),
        style=PREVIEW_BOX_STYLE,
        height=CARD_PREVIEW_SURFACE_HEIGHT,
    )


def select_framework_card() -> rx.Component:
    return rx.box(
        _inject_fw_css,
        rx.box(
            position="absolute",
            top="0",
            right="0",
            width="7rem",
            height="7rem",
            background="radial-gradient(ellipse at top right, rgba(168, 85, 247, 0.10), transparent 60%)",
            border_radius=RADIUS_SM,
            pointer_events="none",
            z_index="1",
        ),
        rx.vstack(
            rx.hstack(
                rx.vstack(
                    rx.text("Select Framework", size="4", weight="bold", color="white"),
                    rx.text(
                        "Define your strategy. Choose from Growth, Value, or Dividend focused models.",
                        size="2",
                        color=TEXT_TERTIARY,
                        line_height="1.65",
                        style=HUB_CARD_TEXT_CLAMP,
                    ),
                    spacing="2",
                    align="start",
                    flex="1",
                    min_width="0",
                ),
                spacing="3",
                align="start",
                width="100%",
            ),
            _framework_preview(),
            rx.spacer(),
            accent_button("Browse Frameworks", href="/framework"),
            spacing="4",
            width="100%",
            height="100%",
        ),
        rx.box(
            position="absolute",
            top="0",
            left="0",
            width="100%",
            height="100%",
            z_index="0",
            cursor="pointer",
            on_click=rx.redirect("/framework"),
        ),
        style=HUB_CARD_STYLE,
        class_name="framework-card",
        # on_mouse_enter / on_mouse_leave removed
    )


def selected_framework_card():
    return rx.cond(
        GlobalFrameworkState.has_selected_framework,
        glass_box(
            rx.vstack(
                rx.text(
                    "Selected Framework",
                    size="1",
                    weight="medium",
                    color=white(0.35),
                ),
                rx.link(
                    rx.text(
                        GlobalFrameworkState.framework_display_name,
                        size="4",
                        weight="bold",
                        color="white",
                        line_height="1.35",
                    ),
                    href="/framework",
                    underline="none",
                ),
                rx.spacer(),
                rx.hstack(
                    rx.vstack(
                        rx.text(
                            "AUTHOR",
                            size="1",
                            weight="bold",
                            color=white(0.2),
                            letter_spacing="0.08em",
                        ),
                        rx.text(
                            rx.cond(
                                GlobalFrameworkState.selected_framework.get("author"),
                                GlobalFrameworkState.selected_framework.get(
                                    "author",
                                    "",
                                ),
                                "—",
                            ),
                            size="2",
                            weight="medium",
                            color=white(0.5),
                            white_space="nowrap",
                            overflow="hidden",
                            text_overflow="ellipsis",
                            width="100%",
                        ),
                        spacing="1",
                        align="start",
                        min_width="0",
                    ),
                    rx.spacer(),
                    accent_button(
                        "Change",
                        icon="refresh-cw",
                        href="/framework",
                        icon_left=True,
                    ),
                    width="100%",
                    align="center",
                ),
                spacing="3",
                align="start",
                width="100%",
            ),
            padding="1.125rem 1.25rem",
            width="100%",
        ),
        glass_box(
            rx.vstack(
                rx.text(
                    "Selected Framework",
                    size="1",
                    weight="medium",
                    color=white(0.22),
                ),
                rx.vstack(
                    rx.text(
                        "No Framework Selected",
                        size="4",
                        weight="bold",
                        color=white(0.28),
                    ),
                    rx.text(
                        "Choose a framework to guide your analysis",
                        size="2",
                        color=white(0.18),
                        line_height="1.6",
                    ),
                    spacing="1",
                    width="100%",
                ),
                rx.spacer(),
                accent_button("Select Framework", href="/framework"),
                spacing="3",
                align="start",
                width="100%",
            ),
            padding="1.125rem 1.25rem",
            width="100%",
        ),
    )
