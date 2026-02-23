"""Financial statement UI component for displaying income statement, balance sheet, and cash flow."""

import reflex as rx
from ..state import FinancialStatementState
from .common_dialog import common_dialog

titles = ["Income\nStatement", "Balance\nSheet", "Cash\nFlow"]


def financial_statements(df_list, show_skeleton=False):
    return rx.vstack(
        *[
            rx.box(
                preview_table(tbl, i, show_skeleton),
                expanded_dialog(tbl, i),
                style={"minWidth": "0"},
            )
            for i, tbl in enumerate(df_list)
        ],
        spacing="4",
        style={"minWidth": "0"},
    )


def _render_header_cell(h):
    return rx.table.column_header_cell(h)


def _render_body_row(data):
    """Render a single row — uses index-based access to avoid lambda closure bug."""
    return rx.table.row(
        rx.foreach(
            data.items(),
            lambda kv: rx.table.cell(
                rx.cond(
                    kv[1] != None,  # noqa: E711
                    rx.text(kv[1]),
                    rx.text(""),
                )
            ),
        )
    )


def preview_table(data, idx, show_skeleton=False):
    title = titles[idx]

    header = rx.vstack(
        rx.text(
            title,
            weight="medium",
            size="7",
            white_space="pre-line",
        ),
        rx.hstack(
            rx.icon(
                "maximize",
                on_click=lambda: FinancialStatementState.expand(idx),
                style={
                    "cursor": rx.cond(show_skeleton, "not-allowed", "pointer"),
                    "userSelect": "none",
                    "color": rx.cond(
                        show_skeleton, rx.color("gray", 6), rx.color("accent", 10)
                    ),
                    "opacity": rx.cond(show_skeleton, "0.5", "1"),
                    "pointerEvents": rx.cond(show_skeleton, "none", "auto"),
                },
            ),
            rx.icon(
                "download",
                on_click=lambda: FinancialStatementState.download_table_csv(data, idx),
                style={
                    "cursor": rx.cond(show_skeleton, "not-allowed", "pointer"),
                    "userSelect": "none",
                    "color": rx.cond(
                        show_skeleton, rx.color("gray", 6), rx.color("accent", 10)
                    ),
                    "opacity": rx.cond(show_skeleton, "0.5", "1"),
                    "pointerEvents": rx.cond(show_skeleton, "none", "auto"),
                },
            ),
            spacing="2",
        ),
        width="12em",
        flex_shrink="0",
        justify="center",
        padding_left="1em",
    )

    if show_skeleton:
        table_content = rx.skeleton(
            height="200px",
            width="43em",
            border_radius="8px",
        )
    else:
        table_content = rx.cond(
            data.length() > 0,
            rx.scroll_area(
                rx.table.root(
                    rx.table.header(
                        rx.table.row(
                            rx.foreach(
                                data[0].keys(),
                                _render_header_cell,
                            )
                        )
                    ),
                    rx.table.body(
                        rx.foreach(
                            data[:5],
                            _render_body_row,
                        )
                    ),
                    size="1",
                    variant="surface",
                    style={
                        "minWidth": "max-content",
                        "width": "auto",
                        "display": "table",
                    },
                ),
                scrollbars="horizontal",
                type="hover",
                style={
                    "height": "auto",
                    "maxWidth": "43em",
                    "position": "relative",
                    "display": "block",
                },
            ),
            rx.text("No data available"),
        )

    return rx.vstack(
        rx.hstack(
            header,
            table_content,
            spacing="4",
            style={"width": "100%", "alignItems": "center"},
        ),
        width="100%",
    )


def _render_expanded_row(data):
    return rx.table.row(
        rx.foreach(
            data.items(),
            lambda kv: rx.table.cell(
                rx.cond(
                    kv[1] != None,  # noqa: E711
                    rx.text(kv[1]),
                    rx.text(""),
                )
            ),
        )
    )


def expanded_dialog(data, idx):
    content = rx.center(
        rx.scroll_area(
            rx.table.root(
                rx.table.header(
                    rx.table.row(
                        rx.foreach(
                            data[0].keys(),
                            _render_header_cell,
                        )
                    )
                ),
                rx.table.body(
                    rx.foreach(
                        data,
                        _render_expanded_row,
                    )
                ),
                size="2",
                variant="surface",
                style={"fontSize": "12px"},
            ),
            style={
                "height": "67vh",
                "width": "90vw",
            },
            scrollbars="both",
        ),
        width="100%",
    )

    return common_dialog(
        content=content,
        is_open=FinancialStatementState.expanded_table == idx,
        on_close=FinancialStatementState.close,
        on_open_change=FinancialStatementState.handle_dialog_open,
        width="90vw",
        height="80vh",
        max_width="90vw",
        padding="1.5rem",
        title=["Income Statement", "Balance Sheet", "Cash Flow"][idx],
    )
