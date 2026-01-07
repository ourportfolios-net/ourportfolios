"""Financial statement UI component for displaying income statement, balance sheet, and cash flow."""

import reflex as rx
from ..state import FinancialStatementState
from .dialog import common_dialog

titles = ["Income\nStatement", "Balance\nSheet", "Cash\nFlow"]


def financial_statements(df_list, show_skeleton=False):
    """
    Display financial statements with optional skeleton loading state.

    Args:
        df_list: List of dataframes [income_statement, balance_sheet, cash_flow]
        show_skeleton: If True, show skeleton placeholders for tables
    """
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


def preview_table(data, idx, show_skeleton=False):
    title = titles[idx]

    # Always show the title and buttons
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

    # Table content - either skeleton or actual data
    table_content = rx.cond(
        show_skeleton,
        # Skeleton for loading state - simple rectangle
        rx.skeleton(
            height="200px",
            width="43em",
            border_radius="8px",
        ),
        # Actual table or "No data available"
        rx.cond(
            data.length() > 0,
            rx.scroll_area(
                rx.table.root(
                    rx.table.header(
                        rx.table.row(
                            rx.foreach(
                                data[0].keys(),
                                lambda h: rx.table.column_header_cell(h),
                            )
                        )
                    ),
                    rx.table.body(
                        rx.foreach(
                            data[:5],
                            lambda row: rx.table.row(
                                rx.foreach(
                                    data[0].keys(),
                                    lambda h: rx.table.cell(
                                        rx.text(row[h])
                                        if row[h] is not None
                                        else rx.text("")
                                    ),
                                )
                            ),
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
        ),
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


def expanded_dialog(data, idx):
    content = rx.center(
        rx.scroll_area(
            rx.table.root(
                rx.table.header(
                    rx.table.row(
                        rx.foreach(
                            data[0].keys(),
                            lambda h: rx.table.column_header_cell(h),
                        )
                    )
                ),
                rx.table.body(
                    rx.foreach(
                        data,
                        lambda row: rx.table.row(
                            rx.foreach(
                                data[0].keys(),
                                lambda h: rx.table.cell(
                                    rx.cond(
                                        row[h] is not None,
                                        rx.text(row[h]),
                                        rx.text(""),
                                    )
                                ),
                            )
                        ),
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
