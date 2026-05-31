"""Graph page state — interactive Cytoscape.js knowledge graph visualization.

Contains the GraphState class, styling constants, and ourgraph bridge.
"""

from __future__ import annotations

import json
import logging
from typing import Any

import reflex as rx

from ourportfolios.ui.theme.colors import blue, green, purple, red

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Optional ourgraph import — gracefully handled if not installed
# ---------------------------------------------------------------------------

_OURGRAPH_AVAILABLE = False
_get_settings = None
GraphQueries = None  # type: ignore[assignment]

try:
    from ourgraph.config import get_settings as _gs
    from ourgraph.graph.queries import GraphQueries as _GQ

    _get_settings = _gs
    GraphQueries = _GQ
    _OURGRAPH_AVAILABLE = True
except ImportError:
    logger.warning("ourgraph library not available — graph page will show placeholder")


# ---------------------------------------------------------------------------
# Node styling constants
# ---------------------------------------------------------------------------

_NODE_COLORS: dict[str, str] = {
    "Company": blue(0.85),
    "Person": green(0.85),
    "Sector": "rgba(249, 115, 22, 0.85)",
    "Industry": "rgba(249, 115, 22, 0.85)",
    "MacroIndicator": red(0.85),
    "Country": purple(0.85),
}

_NODE_SHAPES: dict[str, str] = {
    "Company": "ellipse",
    "Person": "diamond",
    "Sector": "round-rectangle",
    "Industry": "round-rectangle",
    "MacroIndicator": "triangle",
    "Country": "hexagon",
}

# Visual overrides for company_type property (sub-property of Company nodes)
_COMPANY_TYPE_COLORS: dict[str, str] = {
    "listed": "rgba(59, 130, 246, 0.9)",  # bright blue — main tickers
    "subsidiary": "rgba(100, 116, 139, 0.5)",  # muted gray — subsidiary/affiliate
    "audit_firm": "rgba(20, 184, 166, 0.7)",  # teal — audit firms
}

_REL_COLORS: dict[str, str] = {
    "HOLDS_STAKE_IN": "#64748b",
    "SUBSIDIARY_OF": "#8b5cf6",
    "COMPETES_WITH": "#ef4444",
    "IS_OFFICER": "#22c55e",
    "IS_BOARD_MEMBER": "#22c55e",
    "IS_FOUNDER": "#22c55e",
    "IS_EXECUTIVE": "#22c55e",
    "BELONGS_TO": "#475569",
    "BELONGS_TO_INDUSTRY": "#475569",
    "AFFECTS_SECTOR": "#f97316",
    "AFFECTS_INDUSTRY": "#f97316",
    "HAS_MACRO_INDICATOR": "#ef4444",
    "AUDITED_BY": "#14b8a6",
    # Phase 2 relationships
    "RELATED_PARTY_TRANSACTION": "#f59e0b",
    "GUARANTEES": "#ec4899",
    "LENDS_TO": "#06b6d4",
    "HAS_JOINT_VENTURE_WITH": "#8b5cf6",
    "UNDERWRITTEN_BY": "#f97316",
    "HAS_BUSINESS_COOPERATION": "#10b981",
    "STATE_OWNS": "#3b82f6",
}

_REL_STYLES: dict[str, str] = {
    "HOLDS_STAKE_IN": "solid",
    "SUBSIDIARY_OF": "dotted",
    "COMPETES_WITH": "dashed",
    "IS_OFFICER": "solid",
    "IS_BOARD_MEMBER": "solid",
    "IS_FOUNDER": "solid",
    "IS_EXECUTIVE": "solid",
    "BELONGS_TO": "solid",
    "BELONGS_TO_INDUSTRY": "solid",
    "AFFECTS_SECTOR": "dashed",
    "AFFECTS_INDUSTRY": "dashed",
    "HAS_MACRO_INDICATOR": "dotted",
    "AUDITED_BY": "solid",
    # Phase 2 relationships
    "RELATED_PARTY_TRANSACTION": "dashed",
    "GUARANTEES": "dotted",
    "LENDS_TO": "solid",
    "HAS_JOINT_VENTURE_WITH": "dashed",
    "UNDERWRITTEN_BY": "dotted",
    "HAS_BUSINESS_COOPERATION": "dashed",
    "STATE_OWNS": "solid",
}


# ---------------------------------------------------------------------------
# Edge helpers
# ---------------------------------------------------------------------------

_EDGE_LABELS: dict[str, str] = {
    "HOLDS_STAKE_IN": "holds stake in",
    "SUBSIDIARY_OF": "subsidiary",
    "COMPETES_WITH": "competes",
    "IS_OFFICER": "officer",
    "IS_BOARD_MEMBER": "board member",
    "IS_FOUNDER": "founder",
    "IS_EXECUTIVE": "executive",
    "BELONGS_TO": "belongs to",
    "BELONGS_TO_INDUSTRY": "belongs to",
    "AFFECTS_SECTOR": "affects",
    "AFFECTS_INDUSTRY": "affects",
    "HAS_MACRO_INDICATOR": "macro",
    "AUDITED_BY": "audited by",
    "RELATED_PARTY_TRANSACTION": "related party",
    "GUARANTEES": "guarantees",
    "LENDS_TO": "lends to",
    "HAS_JOINT_VENTURE_WITH": "joint venture",
    "UNDERWRITTEN_BY": "underwritten by",
    "HAS_BUSINESS_COOPERATION": "cooperation",
    "STATE_OWNS": "state owns",
}


def _format_edge_value(key: str, val: object) -> str:
    """Format an edge property value for display."""
    s = str(val)
    lower = key.lower()
    if "_percent" in lower or lower == "own_percent":
        try:
            return f"{float(s):.1f}%"
        except (ValueError, TypeError):
            return s
    if lower in ("amount", "issue_amount"):
        try:
            return f"{float(s):,.0f}"
        except (ValueError, TypeError):
            return s
    if "date" in lower:
        return str(val)[:10]
    if lower == "description":
        return str(val)[:200]
    return str(val)[:100] if val is not None else "—"


def _format_edge_detail(rel_type: str, props: dict) -> str:
    """Build a concise detail string for a relationship card."""
    stake = props.get("stake_percent")
    own = props.get("ownership_percent")
    if stake is not None:
        return f"{float(stake):.1f}% stake"
    if own is not None:
        return f"{float(own):.1f}% ownership"
    # Financial-statement edges: surface the statement name / period
    stmt = props.get("statement") or props.get("statement_type") or props.get("type")
    quarter = props.get("quarter") or props.get("period")
    year = props.get("year") or props.get("fiscal_year")
    if stmt:
        parts = [str(stmt)]
        if quarter:
            parts.append(str(quarter))
        if year:
            parts.append(str(year))
        return " ".join(parts)
    # Indicator edges
    ind = props.get("indicator_name") or props.get("name")
    val = props.get("value")
    if ind:
        base = str(ind)
        if val is not None:
            base += f": {val}"
        return base
    # Fallback: role / title
    role = props.get("role") or props.get("title") or props.get("position")
    if role:
        return str(role)
    desc = props.get("description")
    if desc:
        return str(desc)[:80]
    return ""


# ---------------------------------------------------------------------------
# GraphState
# ---------------------------------------------------------------------------


class GraphState(rx.State):
    """State for the interactive knowledge graph page."""

    # ── Graph data ──────────────────────────────────────────────────────────
    graph_json: str = "{}"
    loading: bool = True
    error: str = ""

    # ── Selection ───────────────────────────────────────────────────────────
    selected_node_id: str = ""
    selected_node_type: str = ""
    selected_node_title: str = ""
    selected_node_subtitle: str = ""
    selected_node_ticker: str = ""
    selected_prop_rows: list[list[str]] = []
    # Each edge row: [edge_id, direction("in"|"out"), rel_label, other_name, detail]
    selected_edge_rows: list[list[str]] = []

    # ── Edge selection ──────────────────────────────────────────────────────
    selected_edge_id: str = ""
    selected_edge_source_id: str = ""
    selected_edge_target_id: str = ""
    selected_edge_source_name: str = ""
    selected_edge_target_name: str = ""
    selected_edge_rel_type: str = ""
    selected_edge_label: str = ""
    selected_edge_prop_rows: list[list[str]] = []

    # ── Filters ─────────────────────────────────────────────────────────────
    search_query: str = ""
    show_ownership: bool = True
    show_competition: bool = True
    show_roles: bool = True
    show_industry: bool = True
    show_macro: bool = False

    # ── Visibility toggles (eye / eye-off icons) ────────────────────────────
    hidden_nodes: list[str] = []
    hidden_edges: list[str] = []

    # ── Internal ────────────────────────────────────────────────────────────
    _raw_graph: dict[str, Any] = {}

    @rx.var
    def node_count(self) -> int:
        """Number of nodes in the current graph."""
        try:
            data = json.loads(self.graph_json)
            return len(data.get("nodes", []))
        except (json.JSONDecodeError, TypeError):
            return 0

    @rx.var
    def edge_count(self) -> int:
        """Number of edges in the current graph."""
        try:
            data = json.loads(self.graph_json)
            return len(data.get("edges", []))
        except (json.JSONDecodeError, TypeError):
            return 0

    @rx.var
    def has_selection(self) -> bool:
        """Whether a node or edge is currently selected."""
        return bool(self.selected_node_id or self.selected_edge_id)

    @rx.var
    def edge_source_hidden(self) -> bool:
        """Whether the selected edge's source node is hidden."""
        return self.selected_edge_source_id in self.hidden_nodes

    @rx.var
    def edge_target_hidden(self) -> bool:
        """Whether the selected edge's target node is hidden."""
        return self.selected_edge_target_id in self.hidden_nodes

    @rx.var
    def selected_node_hidden(self) -> bool:
        """Whether the selected node is hidden."""
        return self.selected_node_id in self.hidden_nodes

    # ── Lifecycle ───────────────────────────────────────────────────────────

    def on_mount(self):
        """Initialize and load graph data."""
        logger.info("GraphState.on_mount called")
        return [GraphState.load_graph]  # type: ignore[return-value]

    def on_unmount(self):
        """Clean up."""
        self._raw_graph = {}

    # ── Setters ─────────────────────────────────────────────────────────────

    @rx.event
    def set_search_query(self, value: str) -> None:
        """Update search query and apply JS filter."""
        self.search_query = value
        return rx.call_script(  # type: ignore[return-value]
            f"""
            if (typeof window.setSearch === 'function') {{
                window.setSearch({json.dumps(self.search_query)});
            }}
            """,
        )

    @rx.event
    def toggle_ownership(self) -> None:
        """Toggle ownership relationship filter."""
        self.show_ownership = not self.show_ownership

    @rx.event
    def toggle_competition(self) -> None:
        """Toggle competition relationship filter."""
        self.show_competition = not self.show_competition

    @rx.event
    def toggle_roles(self) -> None:
        """Toggle roles relationship filter."""
        self.show_roles = not self.show_roles

    @rx.event
    def toggle_industry(self) -> None:
        """Toggle industry relationship filter."""
        self.show_industry = not self.show_industry

    @rx.event
    def toggle_macro(self) -> None:
        """Toggle macro relationship filter."""
        self.show_macro = not self.show_macro

    @rx.event
    def apply_filters(self) -> None:
        """Apply current filters to the JS graph."""
        return rx.call_script(  # type: ignore[return-value]
            f"""
            if (typeof window.filterCy === 'function') {{
                window.filterCy({json.dumps(self.search_query)},
                        {json.dumps(self.show_ownership)},
                        {json.dumps(self.show_competition)},
                        {json.dumps(self.show_roles)},
                        {json.dumps(self.show_industry)},
                        {json.dumps(self.show_macro)});
            }}
            """,
        )

    @rx.event
    def toggle_node_visibility(self, node_id: str) -> None:
        """Toggle visibility of a node in the Cytoscape graph."""
        if not node_id:
            return
        if node_id in self.hidden_nodes:
            self.hidden_nodes = [n for n in self.hidden_nodes if n != node_id]
        else:
            self.hidden_nodes = self.hidden_nodes + [node_id]
        return rx.call_script(
            f"if (typeof window.toggleCyNodeVisibility === 'function') {{"
            f"  window.toggleCyNodeVisibility('{node_id}');"
            f"}}",
        )

    @rx.event
    def toggle_edge_visibility(self, edge_id: str) -> None:
        """Toggle visibility of an edge in the Cytoscape graph."""
        if not edge_id:
            return
        if edge_id in self.hidden_edges:
            self.hidden_edges = [e for e in self.hidden_edges if e != edge_id]
        else:
            self.hidden_edges = self.hidden_edges + [edge_id]
        return rx.call_script(
            f"if (typeof window.toggleCyEdgeVisibility === 'function') {{"
            f"  window.toggleCyEdgeVisibility('{edge_id}');"
            f"}}",
        )

    @rx.event
    def clear_selection(self) -> None:
        """Clear the current node or edge selection."""
        self.selected_node_id = ""
        self.selected_node_type = ""
        self.selected_node_title = ""
        self.selected_node_subtitle = ""
        self.selected_node_ticker = ""
        self.selected_prop_rows = []
        self.selected_edge_rows = []  # type: ignore[assignment]
        self.selected_edge_id = ""
        self.selected_edge_source_id = ""
        self.selected_edge_target_id = ""
        self.selected_edge_source_name = ""
        self.selected_edge_target_name = ""
        self.selected_edge_rel_type = ""
        self.selected_edge_label = ""
        self.selected_edge_prop_rows = []

    @rx.event
    def handle_node_click(self, node_id: str) -> None:
        """Handle a node click from the Cytoscape.js frontend."""
        self.clear_selection()
        self.selected_node_id = node_id

        try:
            data = json.loads(self.graph_json)
        except (json.JSONDecodeError, TypeError):
            return

        for node in data.get("nodes", []):
            if node.get("id") == node_id:
                labels = node.get("labels", [])
                self.selected_node_type = labels[0] if labels else "Unknown"
                props = node.get("properties", {})
                self.selected_node_title = (
                    props.get("name")
                    or props.get("person_name")
                    or props.get("symbol")
                    or node_id
                    or "Unknown"
                )
                self.selected_node_subtitle = self.selected_node_type
                if "Company" in labels and props.get("symbol"):
                    self.selected_node_ticker = props.get("symbol")
                else:
                    self.selected_node_ticker = ""
                self.selected_prop_rows = [
                    [str(k), str(v)[:100] if v is not None else "\u2014"]
                    for k, v in props.items()
                    if k not in ("payload",)
                ]
                break

        # Build structured relationship rows for card display.
        # Each row: [edge_id, direction, rel_label, other_name, detail]
        rows: list[list[str]] = []
        # Build a quick lookup for linked-node names
        node_names: dict[str, str] = {}
        for n in data.get("nodes", []):
            p = n.get("properties", {})
            node_names[n.get("id", "")] = (
                p.get("name") or p.get("person_name") or p.get("symbol") or n.get("id", "")
            )
        for e in data.get("edges", []):
            src = e.get("source", "")
            tgt = e.get("target", "")
            if src != node_id and tgt != node_id:
                continue
            rel_type = e.get("relationship", "UNKNOWN")
            rel_label = _EDGE_LABELS.get(rel_type, rel_type.replace("_", " "))
            ep = e.get("properties", {})
            # Reconstruct the Cytoscape edge ID
            eid = src + "--" + rel_type + "--" + tgt
            sp = ep.get("stake_percent")
            if sp is not None:
                eid += "--" + str(sp)
            # Direction
            if src == node_id:
                direction = "out"
                other_name = node_names.get(tgt, tgt)
            else:
                direction = "in"
                other_name = node_names.get(src, src)
            # Detail line: key property
            detail = _format_edge_detail(rel_type, ep)
            rows.append([eid, direction, rel_label, other_name, detail])
        self.selected_edge_rows = rows

    @rx.event
    def handle_edge_click(self, edge_id: str) -> None:
        """Handle an edge click from the Cytoscape.js frontend."""
        self.clear_selection()
        self.selected_edge_id = edge_id

        try:
            data = json.loads(self.graph_json)
        except (json.JSONDecodeError, TypeError):
            return

        edges = data.get("edges", [])
        nodes = data.get("nodes", [])

        # Build a node-id → properties lookup for source/target names
        node_map: dict[str, dict] = {}
        for n in nodes:
            node_map[n.get("id", "")] = n.get("properties", {})

        def _node_name(nid: str) -> str:
            props = node_map.get(nid, {})
            return (
                props.get("name")
                or props.get("person_name")
                or props.get("symbol")
                or nid
            )

        for e in edges:
            src = e.get("source", "")
            tgt = e.get("target", "")
            rel = e.get("relationship", "")
            props = e.get("properties", {})
            # Reconstruct the Cytoscape edge ID
            candidate = src + "--" + rel + "--" + tgt
            sp = props.get("stake_percent")
            if sp is not None:
                candidate += "--" + str(sp)
            if candidate != edge_id:
                continue

            self.selected_edge_source_id = src
            self.selected_edge_target_id = tgt
            self.selected_edge_rel_type = rel
            self.selected_edge_label = _EDGE_LABELS.get(rel, rel.replace("_", " "))
            self.selected_edge_source_name = _node_name(src) or src
            self.selected_edge_target_name = _node_name(tgt) or tgt

            rows: list[list[str]] = []
            for k, v in props.items():
                if v is None:
                    rows.append([k, "—"])
                else:
                    rows.append([k, _format_edge_value(k, v)])
            self.selected_edge_prop_rows = rows
            return

    @rx.event
    def view_edge_source(self) -> None:
        """Navigate from edge detail to the source node."""
        if self.selected_edge_source_id:
            self.handle_node_click(self.selected_edge_source_id)

    @rx.event
    def view_edge_target(self) -> None:
        """Navigate from edge detail to the target node."""
        if self.selected_edge_target_id:
            self.handle_node_click(self.selected_edge_target_id)

    @rx.event
    def focus_edge(self, edge_id: str) -> None:
        """Zoom the graph to a specific edge and select it."""
        if not edge_id:
            return
        return rx.call_script(
            f"if (typeof window.focusEdge === 'function') {{"
            f"  window.focusEdge('{edge_id}');"
            f"}}",
        )

    @rx.event
    def handle_background_click(self) -> None:
        """Handle a background click — deselect node or edge."""
        self.clear_selection()

    # ── Data loading ────────────────────────────────────────────────────────

    @rx.event(background=True)
    async def load_graph(self) -> None:
        """Load graph data from FalkorDB via ourgraph library."""
        async with self:
            self.loading = True
            self.error = ""

        if not _OURGRAPH_AVAILABLE:
            async with self:
                self.error = (
                    "ourgraph library is not installed. "
                    "Add ourgraph as a dependency to enable the knowledge graph."
                )
                self.loading = False
            return

        try:
            settings = _get_settings()  # type: ignore[misc]
            queries = GraphQueries.from_settings(settings.falkordb)  # type: ignore[misc]

            try:
                graph_data = await queries.export_graph_json(max_edges=2000)
            finally:
                await queries.close()

            json_str = json.dumps(graph_data)

            async with self:
                self.graph_json = json_str
                self._raw_graph = graph_data
                self.loading = False

            yield rx.call_script(
                f"window._graphData = {json_str};"
                f"if (window._tryInitCyGraph) window._tryInitCyGraph();",
            )

        except Exception:
            logger.exception("Failed to load graph data")
            async with self:
                self.error = (
                    "Failed to connect to FalkorDB. "
                    "Ensure the database is running and accessible."
                )
                self.loading = False

    @rx.event
    def refresh_graph(self):
        """Refresh graph data from the database."""
        return GraphState.load_graph
