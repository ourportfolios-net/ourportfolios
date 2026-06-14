"""Graph page state — interactive Cytoscape.js knowledge graph visualization.

Contains the GraphState class, styling constants, and ourgraph bridge.
"""

from __future__ import annotations

import json
import logging
import time
from typing import Any, ClassVar

import reflex as rx

from ourportfolios.ui.theme.colors import blue, green, purple, red

# ourgraph graph_layout functions — imported here for category merge
_format_elements = None
_build_style_json = None
try:
    from ourgraph.graph.graph_layout import build_style_json as _bsj
    from ourgraph.graph.graph_layout import format_elements as _fe
    _format_elements = _fe
    _build_style_json = _bsj
except ImportError:
    pass

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Module-level graph cache (shared across all user sessions)
# Module-level cache uses a mutable container to avoid "global" statements
# ---------------------------------------------------------------------------
_CACHE: dict[str, Any] = {"graph": None, "timestamp": 0.0}
CACHE_TTL_SECONDS: int = 3600  # 1 hour — graph data changes infrequently

# ---------------------------------------------------------------------------
# Optional ourgraph import — gracefully handled if not installed
# ---------------------------------------------------------------------------

_OURGRAPH_AVAILABLE = False
_get_settings = None
GraphQueries = None  # type: ignore[assignment]

try:
    from ourgraph.config import get_settings as _gs
    from ourgraph.graph.queries import GraphQueries as _OurgraphQueries

    _get_settings = _gs
    GraphQueries = _OurgraphQueries
    _OURGRAPH_AVAILABLE = True
except ImportError:
    logger.warning("ourgraph library not available — graph page will show placeholder")


# ---------------------------------------------------------------------------
# Node styling constants
# ---------------------------------------------------------------------------

_NODE_COLORS: dict[str, str] = {
    "Company": blue(0.85),
    "Person": green(0.85),
    "Industry": "rgba(249, 115, 22, 0.85)",
    "MacroIndicator": red(0.85),
    "Country": purple(0.85),
}

_NODE_SHAPES: dict[str, str] = {
    "Company": "ellipse",
    "Person": "diamond",
    "Industry": "round-rectangle",
    "MacroIndicator": "triangle",
    "Country": "hexagon",
}

# Visual overrides for company_type property (sub-property of Company nodes)
_COMPANY_TYPE_COLORS: dict[str, str] = {
    "listed": "rgba(59, 130, 246, 0.9)",  # bright blue — main tickers
    "subsidiary": "rgba(100, 116, 139, 0.5)",  # muted gray — subsidiary/affiliate
}

_REL_COLORS: dict[str, str] = {
    "HOLDS_STAKE_IN": "#64748b",
    "SUBSIDIARY_OF": "#8b5cf6",
    "COMPETES_WITH": "#ef4444",
    "IS_OFFICER": "#22c55e",
    "IS_BOARD_MEMBER": "#22c55e",
    "IS_FOUNDER": "#22c55e",
    "IS_EXECUTIVE": "#22c55e",
    "BELONGS_TO_INDUSTRY": "#475569",
    "AFFECTS_SECTOR": "#f97316",
    "AFFECTS_INDUSTRY": "#f97316",
    "HAS_MACRO_INDICATOR": "#ef4444",
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
    "BELONGS_TO_INDUSTRY": "solid",
    "AFFECTS_SECTOR": "dashed",
    "AFFECTS_INDUSTRY": "dashed",
    "HAS_MACRO_INDICATOR": "dotted",
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
    "BELONGS_TO_INDUSTRY": "belongs to",
    "AFFECTS_SECTOR": "affects",
    "AFFECTS_INDUSTRY": "affects",
    "HAS_MACRO_INDICATOR": "macro",
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
            pass
    elif lower in ("amount", "issue_amount"):
        try:
            return f"{float(s):,.0f}"
        except (ValueError, TypeError):
            pass
    elif "date" in lower:
        return str(val)[:10]
    elif lower == "description":
        return str(val)[:200]
    return str(val)[:100] if val is not None else "—"


def _format_edge_detail(_rel_type: str, props: dict) -> str:
    """Build a concise detail string for a relationship card."""
    stake = props.get("stake_percent")
    if stake is not None:
        return f"{float(stake):.1f}% stake"
    own = props.get("ownership_percent")
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
    # Fallback: role / title / description
    role = (
        props.get("role")
        or props.get("title")
        or props.get("position")
        or props.get("description")
    )
    if role:
        value = str(role)
        _max_desc_len = 80
        return value[:_max_desc_len] if len(value) > _max_desc_len else value
    return ""


# ---------------------------------------------------------------------------
# GraphState
# ---------------------------------------------------------------------------


class GraphState(rx.State):
    """State for the interactive knowledge graph page."""

    def __init__(self, *args: object, **kwargs: object) -> None:
        """Initialize state with empty mutable fields."""
        super().__init__(*args, **kwargs)
        self.selected_prop_rows = []
        self.selected_edge_rows = []
        self.selected_edge_prop_rows = []
        self.hidden_nodes = []
        self.hidden_edges = []

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
    selected_prop_rows: list[list[str]]
    # Each edge row: [edge_id, direction("in"|"out"), rel_label, other_name, detail]
    selected_edge_rows: list[list[str]]

    # ── Edge selection ──────────────────────────────────────────────────────
    selected_edge_id: str = ""
    selected_edge_source_id: str = ""
    selected_edge_target_id: str = ""
    selected_edge_source_name: str = ""
    selected_edge_target_name: str = ""
    selected_edge_rel_type: str = ""
    selected_edge_label: str = ""
    selected_edge_prop_rows: list[list[str]]

    # ── Filters ─────────────────────────────────────────────────────────────
    search_query: str = ""
    show_ownership: bool = True
    show_competition: bool = True
    show_roles: bool = True
    show_industry: bool = True
    show_macro: bool = True

    # ── Node type visibility ──────────────────────────────────────────────
    show_company_nodes: bool = True
    show_person_nodes: bool = False

    show_industry_nodes: bool = True
    show_macro_indicator_nodes: bool = True
    show_country_nodes: bool = True

    # ── Company sub-type ──────────────────────────────────────────────────
    show_subsidiaries: bool = False

    # ── Extended edge categories ──────────────────────────────────────────
    show_related_party: bool = True
    show_guarantees: bool = True
    show_lends_to: bool = True
    show_joint_venture: bool = True
    show_underwritten_by: bool = True
    show_cooperation: bool = True
    show_state_owns: bool = True

    # ── Pagination (lazy edge loading) ──────────────────────────────────────
    page: int = 1
    page_size: int = 500
    has_more: bool = False

    # ── Settings dialog ───────────────────────────────────────────────────
    settings_dialog_open: bool = False
    show_node_types_category: bool = True
    show_edge_categories: bool = True

    # ── Visibility toggles (eye / eye-off icons) ────────────────────────────
    hidden_nodes: list[str]
    hidden_edges: list[str]

    # ── Lazy loading ───────────────────────────────────────────────────────
    categories_loaded: list[str] = []
    category_loading: str = ""

    # ── Visible counts (updated from client-side via _applyFilters) ────────
    visible_node_count: int = 0
    visible_edge_count: int = 0

    @rx.event
    def set_visible_counts(self, value: str):
        """Update visible node/edge counts from the client.

        Receives JSON-encoded ``{"nodes": N, "edges": M}`` from the
        ``_sendVisibleCounts`` JS bridge via the hidden ``__cy_counts`` input.
        """
        try:
            payload = json.loads(value)
            self.visible_node_count = int(payload.get("nodes", 0))
            self.visible_edge_count = int(payload.get("edges", 0))
        except (json.JSONDecodeError, TypeError, ValueError):
            pass

    @rx.var
    def node_count(self) -> int:
        return self.visible_node_count

    @rx.var
    def edge_count(self) -> int:
        return self.visible_edge_count

    @rx.var
    def has_graph_data(self) -> bool:
        """True when graph_json contains actual node elements (fallback for
        visible_node_count which is 0 until client reports back).
        """
        if not self.categories_loaded:
            return False
        try:
            data = json.loads(self.graph_json)
            elements = data.get("elements", [])
            return any(el.get("group") == "nodes" for el in elements)
        except (json.JSONDecodeError, TypeError):
            return None

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

    # ── Setters ─────────────────────────────────────────────────────────────

    @rx.event
    def set_search_query(self, value: str) -> None:
        """Update search query and apply JS filter."""
        self.search_query = value
        q = str(self.search_query)
        return rx.call_script(
            f"""
            if (typeof window.setSearch === 'function') {{
                window.setSearch({json.dumps(q)});
            }}
            """,
        )

    # ── Filter helper: build JS that updates _filterState + calls _applyFilters ─
    def _emit_filter_script(self):
        """Build ``call_script`` JS that updates ``window._filterState`` and
        calls ``window._applyFilters()``.

        IMPORTANT: Reflex state vars return proxy objects, not plain Python
        values.  ``bool()`` and ``str()`` cast these to native types so
        ``json.dumps`` can serialize them.
        """
        # Cast to native Python types before json.dumps
        show_company = bool(self.show_company_nodes)
        show_person = bool(self.show_person_nodes)
        show_industry = bool(self.show_industry_nodes)
        show_macro_ind = bool(self.show_macro_indicator_nodes)
        show_country = bool(self.show_country_nodes)
        show_own = bool(self.show_ownership)
        show_comp = bool(self.show_competition)
        show_roles = bool(self.show_roles)
        show_ind = bool(self.show_industry)
        show_mac = bool(self.show_macro)
        show_rel = bool(self.show_related_party)
        show_guar = bool(self.show_guarantees)
        show_lend = bool(self.show_lends_to)
        show_jv = bool(self.show_joint_venture)
        show_uw = bool(self.show_underwritten_by)
        show_coop = bool(self.show_cooperation)
        show_state = bool(self.show_state_owns)
        show_sub = bool(self.show_subsidiaries)
        search_q = str(self.search_query)

        node_type_json = json.dumps({
            "Company": show_company,
            "Person": show_person,
            "Industry": show_industry,
            "MacroIndicator": show_macro_ind,
            "Country": show_country,
        })

        script = (
            f"(function(){{"
            f"var tryApply = function() {{"
            f"if (typeof window._filterState === 'undefined') {{ return setTimeout(tryApply, 100); }}"
            f"window._filterState.ownership = {json.dumps(show_own)};"
            f"window._filterState.competition = {json.dumps(show_comp)};"
            f"window._filterState.roles = {json.dumps(show_roles)};"
            f"window._filterState.industry = {json.dumps(show_ind)};"
            f"window._filterState.macro = {json.dumps(show_mac)};"
            f"window._filterState.related_party = {json.dumps(show_rel)};"
            f"window._filterState.guarantees = {json.dumps(show_guar)};"
            f"window._filterState.lends_to = {json.dumps(show_lend)};"
            f"window._filterState.joint_venture = {json.dumps(show_jv)};"
            f"window._filterState.underwritten_by = {json.dumps(show_uw)};"
            f"window._filterState.cooperation = {json.dumps(show_coop)};"
            f"window._filterState.state_owns = {json.dumps(show_state)};"
            f"window._filterState.showSubsidiaries = {json.dumps(show_sub)};"
            f"window._filterState.nodeType = {node_type_json};"
            f"window._filterState.search = {json.dumps(search_q)};"
            f"if (typeof window._applyFilters === 'function') window._applyFilters();"
            f"}}; tryApply();"
            f"}})()"
        )
        return rx.call_script(script)

    # ── Generic filter toggle ────────────────────────────────────────────────
    _FILTER_TOGGLE_MAP: ClassVar[dict[str, str]] = {
        "ownership": "show_ownership",
        "competition": "show_competition",
        "roles": "show_roles",
        "industry": "show_industry",
        "macro": "show_macro",
        "company_nodes": "show_company_nodes",
        "person_nodes": "show_person_nodes",

        "industry_nodes": "show_industry_nodes",
        "macro_indicator_nodes": "show_macro_indicator_nodes",
        "country_nodes": "show_country_nodes",
        "subsidiaries": "show_subsidiaries",
        "related_party": "show_related_party",
        "guarantees": "show_guarantees",
        "lends_to": "show_lends_to",
        "joint_venture": "show_joint_venture",
        "underwritten_by": "show_underwritten_by",
        "cooperation": "show_cooperation",
        "state_owns": "show_state_owns",
    }

    @rx.event
    def toggle_filter(self, filter_name: str):
        """Toggle a single filter by name from _FILTER_TOGGLE_MAP."""
        attr = self._FILTER_TOGGLE_MAP[filter_name]
        setattr(self, attr, not getattr(self, attr))
        return self._emit_filter_script()

    # ── Lazy-loading toggles ────────────────────────────────────────────────

    @rx.event
    def set_show_person(self, value: bool):
        """Toggle Person visibility and trigger lazy fetch if needed."""
        self.show_person_nodes = value
        if value and "person" not in self.categories_loaded:
            self.category_loading = "Person"
            return [GraphState.fetch_category("person"), self._emit_filter_script()]
        return self._emit_filter_script()

    @rx.event
    def set_show_subsidiaries(self, value: bool):
        """Toggle Subsidiaries visibility and trigger lazy fetch if needed."""
        self.show_subsidiaries = value
        if value and "subsidiaries" not in self.categories_loaded:
            self.category_loading = "Subsidiaries"
            return [GraphState.fetch_category("subsidiaries"), self._emit_filter_script()]
        return self._emit_filter_script()

    @rx.event(background=True)
    async def fetch_category(self, category: str):
        """Fetch additional data category and merge into existing graph."""
        if category in self.categories_loaded:
            async with self:
                self.category_loading = ""
            return

        try:
            settings = _get_settings()  # type: ignore[misc]
            queries = GraphQueries.from_settings(settings.falkordb)  # type: ignore[misc]
            try:
                category_data = await queries.export_graph_json(
                    max_edges=50000,
                    page=1,
                    page_size=100000,
                    categories=[category],
                )
            finally:
                await queries.close()
        except Exception:
            logger.exception(f"Failed to fetch category '{category}'")
            async with self:
                self.category_loading = ""
            return

        if not category_data:
            async with self:
                self.category_loading = ""
            return

        # Merge new nodes/edges into existing graph_json
        try:
            existing = json.loads(self.graph_json)
        except (json.JSONDecodeError, TypeError):
            existing = {"nodes": [], "edges": []}

        existing_nodes = existing.get("nodes", [])
        existing_edges = existing.get("edges", [])
        new_nodes = category_data.get("nodes", [])
        new_edges = category_data.get("edges", [])
        new_elements = category_data.get("elements", [])

        node_ids: set[str] = {n["id"] for n in existing_nodes}
        merged_nodes = list(existing_nodes)
        for n in new_nodes:
            if n["id"] not in node_ids:
                node_ids.add(n["id"])
                merged_nodes.append(n)

        edge_keys: set[tuple[str, str, str]] = {
            (e["source"], e["relationship"], e["target"]) for e in existing_edges
        }
        merged_edges = list(existing_edges)
        for e in new_edges:
            key = (e["source"], e["relationship"], e["target"])
            if key not in edge_keys:
                edge_keys.add(key)
                merged_edges.append(e)

        # Re-run format_elements on the merged raw data
        merged_raw = {"nodes": merged_nodes, "edges": merged_edges}
        merged_elements = _format_elements(merged_raw) if _format_elements else merged_raw["nodes"] + merged_raw["edges"]
        merged_result = {
            "elements": merged_elements,
            "nodes": merged_nodes,
            "edges": merged_edges,
            "style": _build_style_json() if _build_style_json else {},
        }

        merged_json = json.dumps(merged_result)
        new_elements_json = json.dumps(new_elements)

        async with self:
            self.graph_json = merged_json
            self.categories_loaded = [*self.categories_loaded, category]
            self.category_loading = ""

        cat_label = category.capitalize()
        yield rx.call_script(
            f"window._graphData = {merged_json};"
            f"if (window._cy) {{"
            f"  window.hideCategorySkeleton();"
            f"  window._cy.add({new_elements_json});"
            f"  window._applyFilters();"
            f"}} else if (window._tryInitCyGraph) {{"
            f"  window._tryInitCyGraph();"
            f"}}",
        )

    @rx.event
    def open_settings_dialog(self) -> None:
        """Open the graph settings dialog."""
        self.settings_dialog_open = True

    @rx.event
    def close_settings_dialog(self) -> None:
        """Close the graph settings dialog."""
        self.settings_dialog_open = False

    @rx.event
    def handle_settings_dialog_change(self, *, is_open: bool) -> None:
        """Handle dialog open state change."""
        self.settings_dialog_open = is_open

    @rx.event
    def toggle_node_types_category(self, *, _checked: bool = False):
        """Toggle all node types on/off."""
        self.show_node_types_category = not self.show_node_types_category
        self.show_company_nodes = self.show_node_types_category
        self.show_person_nodes = self.show_node_types_category
        self.show_industry_nodes = self.show_node_types_category
        self.show_macro_indicator_nodes = self.show_node_types_category
        self.show_country_nodes = self.show_node_types_category
        return self._emit_filter_script()

    @rx.event
    def toggle_edge_categories(self, *, _checked: bool = False):
        """Toggle all edge categories on/off."""
        self.show_edge_categories = not self.show_edge_categories
        self.show_ownership = self.show_edge_categories
        self.show_competition = self.show_edge_categories
        self.show_roles = self.show_edge_categories
        self.show_industry = self.show_edge_categories
        self.show_macro = self.show_edge_categories
        self.show_related_party = self.show_edge_categories
        self.show_guarantees = self.show_edge_categories
        self.show_lends_to = self.show_edge_categories
        self.show_joint_venture = self.show_edge_categories
        self.show_underwritten_by = self.show_edge_categories
        self.show_cooperation = self.show_edge_categories
        self.show_state_owns = self.show_edge_categories
        return self._emit_filter_script()

    @rx.event
    def select_all_filters(self):
        """Enable all node types and edge categories."""
        self.show_company_nodes = True
        self.show_person_nodes = True
        self.show_industry_nodes = True
        self.show_macro_indicator_nodes = True
        self.show_country_nodes = True
        self.show_subsidiaries = True
        self.show_ownership = True
        self.show_competition = True
        self.show_roles = True
        self.show_industry = True
        self.show_macro = True
        self.show_related_party = True
        self.show_guarantees = True
        self.show_lends_to = True
        self.show_joint_venture = True
        self.show_underwritten_by = True
        self.show_cooperation = True
        self.show_state_owns = True
        return self._emit_filter_script()

    @rx.event
    def clear_all_filters(self):
        """Disable all node types and edge categories except Companies + inter-company edges."""
        self.show_company_nodes = True
        self.show_person_nodes = False
        self.show_industry_nodes = False
        self.show_macro_indicator_nodes = False
        self.show_country_nodes = False
        self.show_subsidiaries = False
        self.show_ownership = True
        self.show_competition = True
        self.show_roles = False
        self.show_industry = False
        self.show_macro = False
        self.show_related_party = True
        self.show_guarantees = True
        self.show_lends_to = True
        self.show_joint_venture = True
        self.show_underwritten_by = True
        self.show_cooperation = True
        self.show_state_owns = True
        return self._emit_filter_script()

    @rx.event
    def apply_filters(self):
        """Apply current filters to the JS graph."""
        return self._emit_filter_script()

    @rx.event
    def toggle_node_visibility(self, node_id: str) -> None:
        """Toggle visibility of a node in the Cytoscape graph."""
        if not node_id:
            return None
        if node_id in self.hidden_nodes:
            self.hidden_nodes = [n for n in self.hidden_nodes if n != node_id]
        else:
            self.hidden_nodes = [*self.hidden_nodes, node_id]
        return rx.call_script(
            f"if (typeof window.toggleCyNodeVisibility === 'function') {{"
            f"  window.toggleCyNodeVisibility('{node_id}');"
            f"}}",
        )

    @rx.event
    def toggle_edge_visibility(self, edge_id: str) -> None:
        """Toggle visibility of an edge in the Cytoscape graph."""
        if not edge_id:
            return None
        if edge_id in self.hidden_edges:
            self.hidden_edges = [e for e in self.hidden_edges if e != edge_id]
        else:
            self.hidden_edges = [*self.hidden_edges, edge_id]
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
            data = {}
        if not data:
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
                    if k != "payload"
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
                p.get("name")
                or p.get("person_name")
                or p.get("symbol")
                or n.get("id", "")
            )
        for e in data.get("edges", []):
            src = e.get("source", "")
            tgt = e.get("target", "")
            if node_id not in (src, tgt):
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
            data = {}
        if not data:
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
            return None
        return rx.call_script(
            f"if (typeof window.focusEdge === 'function') {{"
            f"  window.focusEdge('{edge_id}');"
            f"}}",
        )

    @rx.event
    def handle_background_click(self) -> None:
        """Handle a background click — deselect node or edge."""
        self.clear_selection()

    # ── Zoom controls ───────────────────────────────────────────────────────

    @rx.event
    def zoom_in(self) -> None:
        """Zoom in the Cytoscape graph."""
        return rx.call_script(
            "if (typeof window.zoomIn === 'function') { window.zoomIn(); }",
        )

    @rx.event
    def zoom_out(self) -> None:
        """Zoom out the Cytoscape graph."""
        return rx.call_script(
            "if (typeof window.zoomOut === 'function') { window.zoomOut(); }",
        )

    @rx.event
    def zoom_fit(self) -> None:
        """Fit the Cytoscape graph to view."""
        return rx.call_script(
            "if (typeof window.zoomFit === 'function') { window.zoomFit(); }",
        )

    # ── Data loading ────────────────────────────────────────────────────────

    async def _fetch_graph_data(self) -> tuple[dict | None, str | None]:
        """Fetch graph data from FalkorDB, bypassing cache.

        Returns:
            (graph_data_dict, None) on success, or (None, error_message) on failure.

        """
        if not _OURGRAPH_AVAILABLE:
            return None, (
                "ourgraph library is not installed. "
                "Add ourgraph as a dependency to enable the knowledge graph."
            )

        try:
            settings = _get_settings()  # type: ignore[misc]
            queries = GraphQueries.from_settings(settings.falkordb)  # type: ignore[misc]
            try:
                graph_data = await queries.export_graph_json(
                    max_edges=50000,
                    page=1,
                    page_size=100000,
                    categories=["base"],
                )
            finally:
                await queries.close()

            _CACHE["graph"] = graph_data
            _CACHE["timestamp"] = time.time()
            return graph_data, None

        except Exception:
            logger.exception("Failed to load graph data")
            return None, (
                "Failed to connect to FalkorDB. "
                "Ensure the database is running and accessible."
            )

    @rx.event(background=True)
    async def load_graph(self) -> None:
        """Load graph data from FalkorDB via ourgraph library."""
        # ── Check module-level cache first ────────────────────────────────────
        cache_graph = _CACHE.get("graph")
        cache_ts: float = _CACHE.get("timestamp", 0.0)  # type: ignore[assignment]
        if cache_graph is not None and time.time() - cache_ts < CACHE_TTL_SECONDS:
            cached_json = json.dumps(cache_graph)
            async with self:
                self.graph_json = cached_json
                self.categories_loaded = ["base"]
                self.loading = False
            yield rx.call_script(
                f"window._graphData = {cached_json};"
                f"if (window._tryInitCyGraph) window._tryInitCyGraph();",
            )
            # Sync filter state — initCyGraph resets _filterState to defaults
            yield self._emit_filter_script()
            return

        async with self:
            self.loading = True
            self.error = ""

        graph_data, error = await self._fetch_graph_data()

        if error:
            async with self:
                self.error = error
                self.loading = False
            return

        json_str = json.dumps(graph_data)
        async with self:
            self.graph_json = json_str
            self.categories_loaded = ["base"]
            self.loading = False

        yield rx.call_script(
            f"window._graphData = {json_str};"
            f"if (window._tryInitCyGraph) window._tryInitCyGraph();",
        )
        # Sync filter state — initCyGraph resets _filterState to defaults
        yield self._emit_filter_script()

    @rx.event(background=True)
    async def refresh_graph(self) -> None:
        """Refresh graph data from the database (bypasses cache)."""
        # Destroy old Cytoscape instance so _tryInitCyGraph re-initializes
        yield rx.call_script(
            "if (window._cy) { window._cy.destroy(); window._cy = null; }",
        )

        async with self:
            _CACHE["graph"] = None
            self.page = 1
            self.loading = True
            self.error = ""

        graph_data, error = await self._fetch_graph_data()

        if error:
            async with self:
                self.error = error
                self.loading = False
            return

        json_str = json.dumps(graph_data)
        async with self:
            self.graph_json = json_str
            self.categories_loaded = ["base"]
            self.loading = False

        yield rx.call_script(
            f"window._graphData = {json_str};"
            f"if (window._tryInitCyGraph) window._tryInitCyGraph();",
        )
        # Re-sync filter state — initCyGraph resets _filterState to defaults,
        # but server-side GraphState vars may differ (user toggled filters off).
        yield self._emit_filter_script()

    @rx.event
    def load_more_edges(self):
        """Load the next page of edges. Gracefully wraps the current data."""
        self.page += 1
        return rx.call_script(  # type: ignore[return-value]
            """
            if (typeof window.appendElements === 'function') {
                window.appendElements(window._fullElements);
            }
            """,
        )
