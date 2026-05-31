"""Graph page UI components — all visual elements for the knowledge graph page."""

from __future__ import annotations

import json

import reflex as rx

from ourportfolios.ui.primitives.button import ghost_button_sm, icon_button_xs
from ourportfolios.ui.primitives.input import search_input_with_icon
from ourportfolios.ui.theme.colors import (
    TEXT_MUTED,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    TEXT_TERTIARY,
    purple,
    red,
    white,
)
from ourportfolios.ui.theme.surfaces import (
    CARD_BG,
    CARD_BORDER,
    CARD_STYLE,
    DIVIDER,
    SURFACE_BG,
    SURFACE_BORDER,
)
from ourportfolios.ui.tokens import (
    RADIUS_CARD,
    RADIUS_SM,
    TRANS_DEFAULT,
)

from ._cytoscape import _CYTOSCAPE_JS
from .state import (
    _COMPANY_TYPE_COLORS,
    _NODE_COLORS,
    _NODE_SHAPES,
    _REL_COLORS,
    _REL_STYLES,
    GraphState,
)

# ── Embedded scripts (loaded once per page mount) ─────────────────────────


def _all_scripts() -> rx.Component:
    """Cytoscape.js CDN + style constants + event bridge + engine."""
    return rx.fragment(
        rx.script(src="https://unpkg.com/cytoscape@3.28.1/dist/cytoscape.min.js"),
        rx.script(
            f"window._nodeColors = {json.dumps(_NODE_COLORS)};\n"
            f"window._companyTypeColors = {json.dumps(_COMPANY_TYPE_COLORS)};\n"
            f"window._nodeShapes = {json.dumps(_NODE_SHAPES)};\n"
            f"window._relColors = {json.dumps(_REL_COLORS)};\n"
            f"window._relStyles = {json.dumps(_REL_STYLES)};",
        ),
        rx.script("""
            window._reflexSend = function(eventName, payload) {
                try {
                    // Route through hidden Reflex inputs/buttons for reliable
                    // event delivery.  Reflex 0.9.x internal dispatch APIs may
                    // silently drop events; native DOM events go through the
                    // normal React pipeline.
                    if (eventName === 'graph_state.handle_edge_click') {
                        var inp = document.getElementById('__cy_edge_id');
                        if (inp) {
                            var nativeInputValueSetter = Object.getOwnPropertyDescriptor(
                                window.HTMLInputElement.prototype, 'value'
                            ).set;
                            nativeInputValueSetter.call(inp, payload.edge_id || '');
                            inp.dispatchEvent(new Event('input', {bubbles: true}));
                        }
                    } else if (eventName === 'graph_state.handle_node_click') {
                        var inp2 = document.getElementById('__cy_node_id');
                        if (inp2) {
                            var setter2 = Object.getOwnPropertyDescriptor(
                                window.HTMLInputElement.prototype, 'value'
                            ).set;
                            setter2.call(inp2, payload.node_id || '');
                            inp2.dispatchEvent(new Event('input', {bubbles: true}));
                        }
                    } else if (eventName === 'graph_state.handle_background_click') {
                        var btn3 = document.getElementById('__cy_bg_btn');
                        if (btn3) { btn3.click(); }
                    }
                } catch(e) { console.error('[cy]', e); }
            };
        """),
        rx.script(_CYTOSCAPE_JS),
        # DOM watcher: initializes Cytoscape when the #cy-graph container
        # appears AND window._graphData has been populated.
        rx.script("""
            window._graphData = null;
            window._tryInitCyGraph = function() {
                var container = document.getElementById('cy-graph');
                if (!container || !window._graphData || !window._graphData.nodes) return;
                if (window._cy) return; // already initialized
                if (typeof window.cytoscape === 'undefined' || typeof window.initCyGraph !== 'function') {
                    setTimeout(window._tryInitCyGraph, 200);
                    return;
                }
                window.initCyGraph(window._graphData);
            };
            // Use MutationObserver to detect when the cy-graph div is inserted.
            (function() {
                var observer = new MutationObserver(function() {
                    if (document.getElementById('cy-graph')) {
                        window._tryInitCyGraph();
                    }
                });
                var startObserving = function() {
                    if (document.body) {
                        observer.observe(document.body, {childList: true, subtree: true});
                    } else {
                        setTimeout(startObserving, 100);
                    }
                };
                startObserving();
                // Also poll as a fallback
                setInterval(function() {
                    if (window._graphData && !window._cy && document.getElementById('cy-graph')) {
                        window._tryInitCyGraph();
                    }
                }, 1000);
            })();
        """),
    )


# ── Graph container ──────────────────────────────────────────────────────


def graph_container() -> rx.Component:
    """Cytoscape.js canvas area with app-integrated surface styling.

    Hidden inputs serve as a bridge from Cytoscape.js tap events
    to the Reflex Python backend. JS sets the input value and
    dispatches an 'input' event; Reflex's on_change fires the
    corresponding state handler.
    """
    return rx.box(
        rx.html(
            '<div id="cy-graph" style="width:100%;height:100%;min-height:480px;"></div>',
        ),
        # Hidden bridge inputs — JS sets value + dispatches input event
        rx.input(
            id="__cy_edge_id",
            value="",
            on_change=GraphState.handle_edge_click,
            style={"display": "none"},
        ),
        rx.input(
            id="__cy_node_id",
            value="",
            on_change=GraphState.handle_node_click,
            style={"display": "none"},
        ),
        rx.button(
            "x",
            id="__cy_bg_btn",
            on_click=GraphState.handle_background_click,
            style={"display": "none"},
        ),
        width="100%",
        flex="1",
        min_height="480px",
        position="relative",
        background=SURFACE_BG,
        border=SURFACE_BORDER,
        border_radius=RADIUS_CARD,
        overflow="hidden",
    )


# ── Header with inline stats ────────────────────────────────────────────


def _stat_chip(icon: str, count: rx.Var[int], label: str) -> rx.Component:
    return rx.hstack(
        rx.icon(icon, size=12, color=white(0.35)),
        rx.text(
            rx.text.span(count, weight="bold", color=TEXT_PRIMARY),
            f" {label}",
            size="1",
            color=TEXT_TERTIARY,
            as_="span",
        ),
        spacing="1",
        align="center",
    )


def page_header() -> rx.Component:
    """Title and live node/edge stats in one compact block."""
    return rx.hstack(
        rx.hstack(
            rx.icon("share-2", size=20, color=purple(0.65)),
            rx.heading(
                "Knowledge Graph",
                size="5",
                weight="bold",
                color=TEXT_PRIMARY,
                letter_spacing="tight",
            ),
            spacing="2",
            align="center",
        ),
        rx.spacer(),
        rx.hstack(
            _stat_chip("circle", GraphState.node_count, "nodes"),
            rx.divider(orientation="vertical", height="1rem", border_color=DIVIDER),
            _stat_chip("minus", GraphState.edge_count, "edges"),
            spacing="3",
            align="center",
            padding="0.4rem 0.85rem",
            border_radius=RADIUS_SM,
            background=white(0.025),
            border=f"1px solid {white(0.04)}",
        ),
        spacing="4",
        align="center",
        width="100%",
    )


# ── Pill toggles (replace checkboxes) ───────────────────────────────────


def _pill_toggle(
    icon_name: str,
    label: str,
    active: rx.Var[bool],
    on_toggle: rx.event.EventHandler,
) -> rx.Component:
    """A pill-shaped toggle shown in the filter bar."""
    return rx.box(
        rx.hstack(
            rx.icon(icon_name, size=12),
            rx.text(label, size="1"),
            spacing="1",
            align="center",
        ),
        padding_x="0.55rem",
        padding_y="0.25rem",
        border_radius=RADIUS_SM,
        cursor="pointer",
        transition=TRANS_DEFAULT,
        background=rx.cond(active, white(0.08), white(0.02)),
        border=rx.cond(
            active,
            f"1px solid {white(0.18)}",
            f"1px solid {white(0.05)}",
        ),
        color=rx.cond(active, "white", white(0.5)),
        font_weight=rx.cond(active, "600", "400"),
        _hover={"background": white(0.08), "color": "white"},
        on_click=[on_toggle, GraphState.apply_filters],
    )


def filter_bar() -> rx.Component:
    """Pill-style filter toggles + search input using the shared search primitive."""
    return rx.hstack(
        rx.hstack(
            _pill_toggle(
                "link",
                "Ownership",
                GraphState.show_ownership,
                GraphState.toggle_ownership,
            ),
            _pill_toggle(
                "swords",
                "Compete",
                GraphState.show_competition,
                GraphState.toggle_competition,
            ),
            _pill_toggle(
                "users",
                "People",
                GraphState.show_roles,
                GraphState.toggle_roles,
            ),
            _pill_toggle(
                "factory",
                "Industry",
                GraphState.show_industry,
                GraphState.toggle_industry,
            ),
            _pill_toggle(
                "globe",
                "Macro",
                GraphState.show_macro,
                GraphState.toggle_macro,
            ),
            spacing="2",
            flex_wrap="wrap",
        ),
        rx.spacer(),
        rx.hstack(
            search_input_with_icon(
                placeholder="Filter nodes…",
                value=GraphState.search_query,
                on_change=GraphState.set_search_query,
                width="100%",
                max_width="220px",
                flex_shrink="0",
            ),
            icon_button_xs("rotate-cw", size=16, on_click=GraphState.refresh_graph),
            spacing="2",
            align="center",
        ),
        spacing="3",
        align="center",
        width="100%",
        flex_wrap="wrap",
    )


# ── Loading / Error / Empty ─────────────────────────────────────────────


def loading_view() -> rx.Component:
    return rx.box(
        rx.skeleton(width="100%", height="100%", border_radius=RADIUS_CARD),
        **{k: v for k, v in CARD_STYLE.items() if k != "min_height"},
        width="100%",
        flex="1",
        min_height="480px",
    )


def error_view() -> rx.Component:
    return rx.center(
        rx.vstack(
            rx.icon("triangle-alert", size=28, color=red(0.65)),
            rx.text(
                "Unable to load graph",
                size="3",
                weight="medium",
                color=white(0.75),
            ),
            rx.text(
                GraphState.error,
                size="1",
                color=TEXT_MUTED,
                max_width="360px",
                text_align="center",
            ),
            rx.button(
                rx.hstack(
                    rx.icon("refresh-cw", size=12),
                    rx.text("Retry"),
                    spacing="2",
                ),
                on_click=GraphState.refresh_graph,
                color_scheme="purple",
                variant="soft",
                size="1",
                margin_top="0.5rem",
            ),
            spacing="3",
            align="center",
        ),
        **{k: v for k, v in CARD_STYLE.items() if k != "min_height"},
        width="100%",
        flex="1",
        min_height="480px",
    )


def empty_view() -> rx.Component:
    return rx.center(
        rx.vstack(
            rx.icon("share-2", size=28, color=white(0.1)),
            rx.text("No graph data", size="3", color=white(0.35)),
            rx.text(
                "Run the ourgraph pipeline to populate the knowledge graph.",
                size="1",
                color=TEXT_MUTED,
            ),
            rx.button(
                rx.hstack(
                    rx.icon("refresh-cw", size=12),
                    rx.text("Load Graph"),
                    spacing="2",
                ),
                on_click=GraphState.refresh_graph,
                color_scheme="purple",
                variant="soft",
                size="1",
                margin_top="0.75rem",
            ),
            spacing="3",
            align="center",
        ),
        **{k: v for k, v in CARD_STYLE.items() if k != "min_height"},
        width="100%",
        flex="1",
        min_height="480px",
    )


# ── Node detail panel ───────────────────────────────────────────────────


def _prop_row(row: list[str]) -> rx.Component:
    key, val = row[0], row[1]
    return rx.hstack(
        rx.text(key, size="1", color=TEXT_TERTIARY, min_width="85px", flex_shrink="0"),
        rx.text(val, size="1", color=TEXT_PRIMARY),
        spacing="2",
        align="start",
        padding_y="0.15rem",
        width="100%",
    )


def _rel_card(row: list[str]) -> rx.Component:
    """A single relationship card — clickable, zooms to the edge.

    row: [edge_id, direction("in"|"out"), rel_label, other_name, detail]

    The text flows naturally:
      → holds stake in  XYZ Corp · 15.0% stake    (outgoing: this node → other)
      ← subsidiary of  ABC Corp · 54.76%          (incoming: other → this node)
    """
    return rx.box(
        rx.hstack(
            rx.icon(
                rx.cond(row[1] == "in", "arrow-left", "arrow-right"),  # type: ignore[index]
                size=13,
                color=white(0.3),
                flex_shrink="0",
            ),
            rx.text(
                row[2],  # type: ignore[index]
                size="1",
                weight="medium",
                color=TEXT_PRIMARY,
                flex_shrink="0",
            ),
            rx.text(
                row[3],  # type: ignore[index]
                size="1",
                color=white(0.55),
            ),
            rx.cond(
                row[4] != "",  # type: ignore[index]
                rx.text(row[4], size="1", color=TEXT_TERTIARY, flex_shrink="0"),  # type: ignore[index]
                rx.fragment(),
            ),
            spacing="1",
            align="center",
            width="100%",
            flex_wrap="wrap",
        ),
        padding="0.4rem 0.55rem",
        border_radius=RADIUS_SM,
        background=white(0.02),
        border=f"1px solid {white(0.04)}",
        cursor="pointer",
        _hover={"background": white(0.05), "border_color": white(0.1)},
        on_click=GraphState.focus_edge(row[0]),  # type: ignore[index, arg-type]
        width="100%",
    )


def _eye_button(hidden: rx.Var[bool], on_toggle: rx.event.EventHandler) -> rx.Component:
    """Eye / eye-off toggle using icon_button_xs — same as the refresh button."""
    return rx.cond(
        hidden,
        icon_button_xs("eye-off", size=14, on_click=on_toggle),
        icon_button_xs("eye", size=14, on_click=on_toggle),
    )


def _node_detail_content() -> rx.Component:
    """Content shown when a node is selected — title, type, relationships."""
    return rx.vstack(
        # Header: title + eye button
        rx.hstack(
            rx.heading(
                GraphState.selected_node_title,
                size="3",
                weight="bold",
                color=TEXT_PRIMARY,
            ),
            rx.spacer(),
            _eye_button(
                GraphState.selected_node_hidden,
                GraphState.toggle_node_visibility(GraphState.selected_node_id),  # type: ignore[arg-type]
            ),
            align="center",
            width="100%",
        ),
        # Ticker link (Company nodes only)
        rx.cond(
            GraphState.selected_node_ticker != "",
            rx.link(
                ghost_button_sm(
                    rx.hstack(
                        rx.icon("external-link", size=10),
                        rx.text("Analyze", size="1"),
                        spacing="1",
                    ),
                ),
                href=f"/tickers/{GraphState.selected_node_ticker}",
            ),
            rx.fragment(),
        ),
        # Relationships
        rx.vstack(
            rx.text("Relationships", size="1", weight="medium", color=TEXT_SECONDARY),
            rx.scroll_area(
                rx.cond(
                    GraphState.selected_edge_rows.length() > 0,
                    rx.vstack(
                        rx.foreach(GraphState.selected_edge_rows, _rel_card),  # type: ignore[arg-type]
                        spacing="2",
                        width="100%",
                    ),
                    rx.text(
                        "(no relationships)",
                        size="1",
                        color=TEXT_MUTED,
                        font_style="italic",
                    ),
                ),
                type="auto",
                scrollbars="vertical",
                style={"maxHeight": "340px"},
            ),
            spacing="2",
            width="100%",
        ),
        spacing="4",
        align="start",
        width="100%",
    )


def _edge_detail_content() -> rx.Component:
    """Content shown when an edge is selected — label, connection, properties."""
    return rx.vstack(
        # Header
        rx.hstack(
            rx.vstack(
                rx.heading(
                    GraphState.selected_edge_label,
                    size="3",
                    weight="bold",
                    color=TEXT_PRIMARY,
                    text_transform="capitalize",
                ),
                rx.text(
                    GraphState.selected_edge_rel_type.replace("_", " "),
                    size="1",
                    color=TEXT_TERTIARY,
                ),
                spacing="0",
                align="start",
            ),
            rx.spacer(),
            _eye_button(
                GraphState.edge_source_hidden,
                GraphState.toggle_node_visibility(GraphState.selected_edge_source_id),  # type: ignore[arg-type]
            ),
            align="start",
            width="100%",
        ),
        # Connection
        rx.vstack(
            rx.text("Connection", size="1", weight="medium", color=TEXT_SECONDARY),
            rx.hstack(
                rx.text(GraphState.selected_edge_source_name, size="1", color=TEXT_PRIMARY, weight="medium"),
                rx.icon("arrow-right", size=12, color=white(0.25)),
                rx.text(GraphState.selected_edge_target_name, size="1", color=TEXT_PRIMARY, weight="medium"),
                spacing="2",
                align="center",
                width="100%",
            ),
            spacing="1",
            width="100%",
        ),
        # Properties
        rx.cond(
            GraphState.selected_edge_prop_rows.length() > 0,
            rx.vstack(
                rx.text("Properties", size="1", weight="medium", color=TEXT_SECONDARY),
                rx.scroll_area(
                    rx.vstack(
                        rx.foreach(GraphState.selected_edge_prop_rows, _prop_row),
                        spacing="0",
                        width="100%",
                    ),
                    type="auto",
                    scrollbars="vertical",
                    style={"maxHeight": "200px"},
                ),
                spacing="2",
                width="100%",
            ),
            rx.fragment(),
        ),
        spacing="4",
        align="start",
        width="100%",
    )


def _empty_detail_content() -> rx.Component:
    """Content shown when nothing is selected."""
    return rx.vstack(
        rx.icon("mouse-pointer-click", size=22, color=white(0.08)),
        rx.text(
            "Click a node or edge to inspect",
            size="1",
            color=TEXT_MUTED,
            text_align="center",
        ),
        spacing="2",
        align="center",
        justify="center",
        width="100%",
        min_height="260px",
    )


def node_detail_panel() -> rx.Component:
    """Side/overlay panel showing selected node or edge details.

    Matches the graph container height via flex stretch on the parent row
    and uses rx.scroll_area for internal scrolling.
    """
    return rx.box(
        rx.scroll_area(
            rx.cond(
                GraphState.selected_node_id != "",
                _node_detail_content(),
                rx.cond(
                    GraphState.selected_edge_id != "",
                    _edge_detail_content(),
                    _empty_detail_content(),
                ),
            ),
            type="auto",
            scrollbars="vertical",
        ),
        padding="1rem",
        width="100%",
        min_height="480px",
        background=CARD_BG,
        border=CARD_BORDER,
        border_radius=RADIUS_CARD,
        overflow="hidden",
    )


# ── Layout composition ──────────────────────────────────────────────────


def _graph_area() -> rx.Component:
    """Graph container with conditional loading / error / empty / graph.

    Declared as a column flex so that children with flex=1 (graph_container,
    loading_view, etc.) fill the available vertical space.  This gives
    the #cy-graph div a computed-height parent, which Cytoscape.js needs.
    """
    return rx.box(
        rx.cond(
            GraphState.loading,
            loading_view(),
            rx.cond(
                GraphState.error != "",
                error_view(),
                rx.cond(
                    (GraphState.node_count == 0) & ~GraphState.loading,
                    empty_view(),
                    graph_container(),
                ),
            ),
        ),
        width="100%",
        flex="1",
        min_height="480px",
        display="flex",
        flex_direction="column",
    )


def main_content() -> rx.Component:
    """Full page composition: header -> filters -> graph + detail panel.

    Uses natural document flow — no fixed heights that would create
    nested scroll contexts.  The graph and detail panel stretch to
    match each other via the flex parent's align-items: stretch.
    """
    return rx.vstack(
        page_header(),
        filter_bar(),
        rx.flex(
            _graph_area(),
            rx.box(
                node_detail_panel(),
                width=rx.breakpoints(initial="100%", lg="260px"),
                flex_shrink="0",
                flex_grow="0",
            ),
            spacing="4",
            direction=rx.breakpoints(initial="column", lg="row"),
            align="stretch",
            width="100%",
        ),
        spacing="4",
        width="100%",
        align="start",
    )
