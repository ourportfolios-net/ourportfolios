"""Graph page UI components — all visual elements for the knowledge graph page."""

from __future__ import annotations

import json
from typing import cast

import reflex as rx

from ourportfolios.components.category_toggle_card import category_toggle_card
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
    BUTTON_GHOST_SM,
    CARD_STYLE,
    MODAL_BG,
    MODAL_PANEL_STYLE,
    SURFACE_BG,
    SURFACE_BORDER,
)
from ourportfolios.ui.tokens import (
    BLUR_DEFAULT,
    RADIUS_CARD,
    RADIUS_SM,
    SHADOW_LG,
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
                console.log('[cy] _reflexSend called:', eventName, JSON.stringify(payload));
                try {
                    if (eventName === 'graph_state.handle_edge_click') {
                        var inp = document.getElementById('__cy_edge_id');
                        console.log('[cy] _reflexSend: found edge input:', !!inp);
                        if (inp) {
                            var nativeInputValueSetter = Object.getOwnPropertyDescriptor(
                                window.HTMLInputElement.prototype, 'value'
                            ).set;
                            nativeInputValueSetter.call(inp, payload.edge_id || '');
                            inp.dispatchEvent(new Event('input', {bubbles: true}));
                            console.log('[cy] _reflexSend: dispatched input on edge input');
                        }
                    } else if (eventName === 'graph_state.handle_node_click') {
                        var inp2 = document.getElementById('__cy_node_id');
                        console.log('[cy] _reflexSend: found node input:', !!inp2);
                        if (inp2) {
                            var setter2 = Object.getOwnPropertyDescriptor(
                                window.HTMLInputElement.prototype, 'value'
                            ).set;
                            setter2.call(inp2, payload.node_id || '');
                            inp2.dispatchEvent(new Event('input', {bubbles: true}));
                            console.log('[cy] _reflexSend: dispatched input on node input');
                        }
                    } else if (eventName === 'graph_state.handle_background_click') {
                        var btn3 = document.getElementById('__cy_bg_btn');
                        if (btn3) { btn3.click(); }
                    } else if (eventName === 'graph_state.set_visible_counts') {
                        var inp4 = document.getElementById('__cy_counts');
                        if (inp4) {
                            var setter4 = Object.getOwnPropertyDescriptor(
                                window.HTMLInputElement.prototype, 'value'
                            ).set;
                            setter4.call(inp4, JSON.stringify(payload));
                            inp4.dispatchEvent(new Event('input', {bubbles: true}));
                        }
                    }
                } catch(e) { console.error('[cy] _reflexSend error:', e); }
            };
        """),
        rx.script(_CYTOSCAPE_JS),
        # DOM watcher: initializes Cytoscape when the #cy-graph container
        # appears AND window._graphData has been populated.
        rx.script("""
            window._graphData = null;
            window._tryInitCyGraph = function() {
                var container = document.getElementById('cy-graph');
                if (!container || !window._graphData) return;
                if (!window._graphData.nodes || window._graphData.nodes.length === 0) return;
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
            })();
        """),
    )


# ── Graph container ──────────────────────────────────────────────────────


def detail_overlay() -> rx.Component:
    """Info overlay — hidden until a node/edge is clicked, then shown at bottom-right."""
    return rx.cond(
        GraphState.has_selection,
        rx.box(
            rx.cond(
                GraphState.selected_node_id != "",
                _node_detail_content(),
                _edge_detail_content(),
            ),
            position="absolute",
            bottom="1rem",
            right="1rem",
            width=rx.breakpoints(initial="calc(100% - 2rem)", sm="360px", md="400px"),
            max_width="calc(100% - 2rem)",
            padding="1.25rem",
            background=MODAL_BG,
            border=f"1px solid {white(0.08)}",
            border_radius=RADIUS_CARD,
            opacity=0.95,
            z_index=50,
            box_shadow=SHADOW_LG,
            backdrop_filter=f"blur({BLUR_DEFAULT})",
        ),
        rx.fragment(),
    )


def graph_container() -> rx.Component:
    """Cytoscape.js canvas area with app-integrated surface styling.

    Hidden inputs serve as a bridge from Cytoscape.js tap events
    to the Reflex Python backend. JS sets the input value and
    dispatches an 'input' event; Reflex's on_change fires the
    corresponding state handler.
    """
    return rx.box(
        rx.html(
            '<div id="cy-graph" style="width:100%;height:100%;min-height:560px;"></div>',
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
        rx.input(
            id="__cy_counts",
            value="",
            on_change=GraphState.set_visible_counts,
            style={"display": "none"},
        ),
        detail_overlay(),
        # Zoom controls (bottom-left)
        rx.box(
            rx.hstack(
                icon_button_xs("zoom-in", size=16, on_click=GraphState.zoom_in),
                icon_button_xs("zoom-out", size=16, on_click=GraphState.zoom_out),
                icon_button_xs("maximize-2", size=16, on_click=GraphState.zoom_fit),
                spacing="1",
                padding="0.35rem",
                border_radius=RADIUS_SM,
                background="rgba(0,0,0,0.6)",
                backdrop_filter=f"blur({BLUR_DEFAULT})",
            ),
            position="absolute",
            bottom="1rem",
            left="1rem",
            z_index=45,
        ),
        # Category loading skeleton (top-center, below hint)
        rx.cond(
            GraphState.category_loading != "",
            rx.box(
                rx.hstack(
                    rx.html(
                        '<span style="display:inline-flex;gap:4px;">'
                        '<span style="width:6px;height:6px;border-radius:50%;background:rgba(255,255,255,0.5);display:inline-block;animation:pulse 1.2s ease-in-out 0s infinite;"></span>'
                        '<span style="width:6px;height:6px;border-radius:50%;background:rgba(255,255,255,0.5);display:inline-block;animation:pulse 1.2s ease-in-out 0.2s infinite;"></span>'
                        '<span style="width:6px;height:6px;border-radius:50%;background:rgba(255,255,255,0.5);display:inline-block;animation:pulse 1.2s ease-in-out 0.4s infinite;"></span>'
                        '</span>'
                        '<style>@keyframes pulse { 0%,100% { opacity:0.2; } 50% { opacity:1; } }</style>',
                    ),
                    rx.text(
                        rx.text.span(GraphState.category_loading),
                        " data loading",
                        size="1",
                        color=white(0.6),
                    ),
                    spacing="2",
                    align="center",
                ),
                position="absolute",
                top="0.5rem",
                left="50%",
                transform="translateX(-50%)",
                z_index=60,
                padding="0.35rem 0.85rem",
                border_radius=RADIUS_SM,
                background="rgba(0,0,0,0.7)",
                backdrop_filter=f"blur({BLUR_DEFAULT})",
                pointer_events="none",
            ),
            rx.fragment(),
        ),
        # Helper hint (top-center)
        rx.cond(
            ~GraphState.has_selection & ~GraphState.loading & (GraphState.error == ""),
            rx.box(
                rx.text(
                    "Rings = industry groups \u00b7 Lines = relationships",
                    size="1",
                    color="rgba(255,255,255,0.3)",
                    font_style="italic",
                ),
                position="absolute",
                top="0.5rem",
                left="50%",
                transform="translateX(-50%)",
                z_index=40,
                padding="0.25rem 0.75rem",
                border_radius=RADIUS_SM,
                background="rgba(0,0,0,0.6)",
                backdrop_filter=f"blur({BLUR_DEFAULT})",
            ),
            rx.fragment(),
        ),
        width="100%",
        height="100%",
        position="relative",
        background=SURFACE_BG,
        border=SURFACE_BORDER,
        border_radius=RADIUS_CARD,
        overflow="hidden",
    )


# ── Header with inline stats ────────────────────────────────────────────


def _stat_chip(icon: str, count: int | rx.Var, label: str) -> rx.Component:
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


def filter_bar() -> rx.Component:
    """Search input + refresh — relationship toggles moved to Settings."""
    return rx.hstack(
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


def _checkbox_row(
    label: str,
    *,
    checked: rx.Var[bool] | bool,
    on_toggle: rx.event.EventHandler,
) -> rx.Component:
    """Create a single checkbox + label row matching the tickers metric checkbox layout."""
    return rx.hstack(
        rx.checkbox(
            checked=checked,
            on_change=on_toggle,
            size="1",
            color_scheme="violet",
        ),
        rx.text(label, size="2", color=white(0.65)),
        spacing="2",
        align="center",
    )


def settings_dialog() -> rx.Component:
    """Render a settings dialog matching the tickers metrics settings dialog structure."""
    return rx.dialog.root(
        rx.dialog.trigger(
            rx.button(
                rx.icon("settings-2", size=14),
                size="2",
                style=BUTTON_GHOST_SM,
                flex_shrink="0",
            ),
        ),
        rx.dialog.content(
            rx.vstack(
                rx.hstack(
                    rx.text("Graph Settings", size="5", weight="bold", color="white"),
                    rx.spacer(),
                    rx.dialog.close(
                        rx.icon(
                            "x",
                            size=18,
                            style={
                                "cursor": "pointer",
                                "color": white(0.4),
                                "transition": "color 0.15s ease",
                                "_hover": {"color": "white"},
                            },
                        ),
                    ),
                    width="100%",
                    align="center",
                    spacing="3",
                ),
                rx.box(height="1px", width="100%", background=white(0.06)),
                rx.scroll_area(
                    rx.box(
                        category_toggle_card(
                            title="Node Types",
                            checked=GraphState.show_node_types_category,
                            on_change=GraphState.toggle_node_types_category,
                            body=rx.box(
                                _checkbox_row("Company", checked=GraphState.show_company_nodes, on_toggle=GraphState.toggle_filter("company_nodes"),
                                ),
                                _checkbox_row("Person", checked=GraphState.show_person_nodes, on_toggle=GraphState.set_show_person,
                                ),
                                _checkbox_row("Industry", checked=GraphState.show_industry_nodes, on_toggle=GraphState.toggle_filter("industry_nodes"),
                                ),
                                _checkbox_row("Macro Indicator", checked=GraphState.show_macro_indicator_nodes, on_toggle=GraphState.toggle_filter("macro_indicator_nodes"),
                                ),
                                _checkbox_row("Country", checked=GraphState.show_country_nodes, on_toggle=GraphState.toggle_filter("country_nodes"),
                                ),
                                _checkbox_row("Subsidiaries", checked=GraphState.show_subsidiaries, on_toggle=GraphState.set_show_subsidiaries,
                                ),
                                display="grid",
                                grid_template_columns="1fr 1fr",
                                gap="0.45em 1em",
                                width="100%",
                            ),
                        ),
                        category_toggle_card(
                            title="Edge Categories",
                            checked=GraphState.show_edge_categories,
                            on_change=GraphState.toggle_edge_categories,
                            body=rx.box(
                                _checkbox_row("Ownership", checked=GraphState.show_ownership, on_toggle=GraphState.toggle_filter("ownership"),
                                ),
                                _checkbox_row("Competition", checked=GraphState.show_competition, on_toggle=GraphState.toggle_filter("competition"),
                                ),
                                _checkbox_row("Roles / People", checked=GraphState.show_roles, on_toggle=GraphState.toggle_filter("roles"),
                                ),
                                _checkbox_row("Industry", checked=GraphState.show_industry, on_toggle=GraphState.toggle_filter("industry"),
                                ),
                                _checkbox_row("Macro", checked=GraphState.show_macro, on_toggle=GraphState.toggle_filter("macro"),
                                ),
                                _checkbox_row("Related Party", checked=GraphState.show_related_party, on_toggle=GraphState.toggle_filter("related_party"),
                                ),
                                _checkbox_row("Guarantees", checked=GraphState.show_guarantees, on_toggle=GraphState.toggle_filter("guarantees"),
                                ),
                                _checkbox_row("Lends To", checked=GraphState.show_lends_to, on_toggle=GraphState.toggle_filter("lends_to"),
                                ),
                                _checkbox_row("Joint Venture", checked=GraphState.show_joint_venture, on_toggle=GraphState.toggle_filter("joint_venture"),
                                ),
                                _checkbox_row("Underwritten By", checked=GraphState.show_underwritten_by, on_toggle=GraphState.toggle_filter("underwritten_by"),
                                ),
                                _checkbox_row("Cooperation", checked=GraphState.show_cooperation, on_toggle=GraphState.toggle_filter("cooperation"),
                                ),
                                _checkbox_row("State Owns", checked=GraphState.show_state_owns, on_toggle=GraphState.toggle_filter("state_owns"),
                                ),
                                display="grid",
                                grid_template_columns="1fr 1fr",
                                gap="0.45em 1em",
                                width="100%",
                            ),
                        ),
                        display="grid",
                        grid_template_columns="repeat(auto-fill, minmax(min(16rem, 100%), 1fr))",
                        gap="0.65em",
                        width="100%",
                    ),
                    type="auto",
                    scrollbars="vertical",
                    style={"height": "65vh"},
                ),
                rx.hstack(
                    rx.spacer(),
                    ghost_button_sm(
                        "Select All",
                        on_click=GraphState.select_all_filters,
                    ),
                    ghost_button_sm(
                        "Clear All",
                        on_click=GraphState.clear_all_filters,
                    ),
                    spacing="2",
                    width="100%",
                    flex_shrink="0",
                ),
                spacing="4",
                width="100%",
                overflow="hidden",
            ),
            width=rx.breakpoints(initial="95vw", md="82vw"),
            max_width="100rem",
            overflow="hidden",
            style={**MODAL_PANEL_STYLE, "overflowX": "hidden"},
        ),
        open=GraphState.settings_dialog_open,
        on_open_change=GraphState.handle_settings_dialog_change,
    )


# ── Loading / Error / Empty ─────────────────────────────────────────────


def loading_view() -> rx.Component:
    return rx.box(
        rx.skeleton(width="100%", height="100%", border_radius=RADIUS_CARD),
        **cast("dict", {k: v for k, v in CARD_STYLE.items() if k != "min_height"}),
        width="100%",
        flex="1",
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
            ghost_button_sm(
                "Retry",
                on_click=GraphState.refresh_graph,
                margin_top="0.5rem",
            ),
            spacing="3",
            align="center",
        ),
        **cast("dict", {k: v for k, v in CARD_STYLE.items() if k != "min_height"}),
        width="100%",
        flex="1",
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
            ghost_button_sm(
                "Retry",
                on_click=GraphState.refresh_graph,
                margin_top="0.75rem",
            ),
            spacing="3",
            align="center",
        ),
        **cast("dict", {k: v for k, v in CARD_STYLE.items() if k != "min_height"}),
        width="100%",
        flex="1",
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
    """Build a single relationship card — clickable, zooms to the edge.

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
        # NOTE: row[0] subscript in foreach may not compile correctly in Reflex.
        # Re-enable focus-on-click once verified or use a bridge pattern.
        # on_click=GraphState.focus_edge(row[0]),
        cursor="default",
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
        # Header row: title + Analyze button --- eye + X
        rx.hstack(
            rx.heading(
                GraphState.selected_node_title,
                size="5",
                weight="bold",
                color=TEXT_PRIMARY,
            ),
            rx.cond(
                GraphState.selected_node_ticker != "",
                rx.link(
                    rx.button(
                        rx.hstack(
                            rx.icon("external-link", size=12),
                            rx.text("Analyze", size="1"),
                            spacing="1",
                            align="center",
                        ),
                        size="1",
                        style=BUTTON_GHOST_SM,
                        display="inline-flex",
                        align_items="center",
                    ),
                    href=f"/tickers/{GraphState.selected_node_ticker}",
                ),
                rx.fragment(),
            ),
            rx.spacer(),
            _eye_button(
                GraphState.selected_node_hidden,
                GraphState.toggle_node_visibility(GraphState.selected_node_id),  # type: ignore[arg-type]
            ),
            icon_button_xs("x", size=14, on_click=GraphState.handle_background_click),
            spacing="2",
            align="center",
            width="100%",
        ),
        # Relationships
        rx.vstack(
            rx.text("Relationships", size="1", weight="medium", color=TEXT_SECONDARY),
            rx.scroll_area(
                rx.cond(
                    GraphState.has_selected_edge_rows,
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
                type="hover",
                scrollbars="vertical",
                style={"maxHeight": "340px"},
            ),
            spacing="2",
            width="100%",
        ),
        spacing="3",
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
            icon_button_xs("x", size=14, on_click=GraphState.handle_background_click),
            align="center",
            width="100%",
        ),
        # Connection
        rx.vstack(
            rx.text("Connection", size="1", weight="medium", color=TEXT_SECONDARY),
            rx.hstack(
                rx.text(
                    GraphState.selected_edge_source_name,
                    size="1",
                    color=TEXT_PRIMARY,
                    weight="medium",
                ),
                rx.icon("arrow-right", size=12, color=white(0.25)),
                rx.text(
                    GraphState.selected_edge_target_name,
                    size="1",
                    color=TEXT_PRIMARY,
                    weight="medium",
                ),
                spacing="2",
                align="center",
                width="100%",
            ),
            spacing="1",
            width="100%",
        ),
        # Properties
        rx.cond(
            GraphState.has_selected_edge_prop_rows,
            rx.vstack(
                rx.text("Properties", size="1", weight="medium", color=TEXT_SECONDARY),
                rx.scroll_area(
                    rx.vstack(
                        rx.foreach(GraphState.selected_edge_prop_rows, _prop_row),
                        spacing="0",
                        width="100%",
                    ),
                    type="hover",
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
                    (~GraphState.has_graph_data) & ~GraphState.loading,
                    empty_view(),
                    graph_container(),
                ),
            ),
        ),
        width="100%",
        flex="1",
        min_height="0",  # was "560px" — let flex parent control
        display="flex",
        flex_direction="column",
    )


def main_content() -> rx.Component:
    """Full page composition: header -> filters -> full-width graph.

    The graph card spans the entire page width with the detail panel
    as a floating overlay at the bottom-right when a node/edge is clicked.
    """
    return rx.vstack(
        page_header(),
        filter_bar(),
        settings_dialog(),
        _graph_area(),
        spacing="4",
        width="100%",
        align="start",
        flex="1",
        min_height="0",
    )
