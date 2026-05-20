"""Layout primitives for consistent spacing, stacking, and structure."""

from __future__ import annotations

import reflex as rx

from ourportfolios.ui.theme.surfaces import DIVIDER
from ourportfolios.ui.tokens import HOME_CONTENT_MAX_WIDTH, HOME_CONTENT_WIDTH


def vstack(
    *children: rx.Component,
    spacing: str = "4",
    **props: object,
) -> rx.Component:
    """Vertical stack with consistent defaults.

    Args:
        children: Child components.
        spacing: Gap between children.
        **props: Additional Reflex vstack props.

    """
    return rx.vstack(*children, **{"spacing": spacing, **props})


def hstack(
    *children: rx.Component,
    spacing: str = "3",
    **props: object,
) -> rx.Component:
    """Horizontal stack with consistent defaults.

    Args:
        children: Child components.
        spacing: Gap between children.
        **props: Additional Reflex hstack props.

    """
    return rx.hstack(*children, **{"spacing": spacing, **props})


def section_stack(
    *children: rx.Component,
    **props: object,
) -> rx.Component:
    """Section-level vertical stack with section gap.

    Args:
        children: Child components.
        **props: Additional Reflex vstack props.

    """
    return rx.vstack(*children, **{"spacing": "5", "align": "start", "width": "100%", **props})


def content_stack(
    *children: rx.Component,
    **props: object,
) -> rx.Component:
    """Content-level vertical stack with tighter spacing.

    Args:
        children: Child components.
        **props: Additional Reflex vstack props.

    """
    return rx.vstack(*children, **{"spacing": "4", "align": "start", "width": "100%", **props})


def inline_cluster(
    *children: rx.Component,
    **props: object,
) -> rx.Component:
    """Inline cluster for badges, chips, and small elements.

    Args:
        children: Child components.
        **props: Additional Reflex hstack props.

    """
    return rx.hstack(*children, **{"spacing": "2", "align": "center", **props})


def flex_row(
    *children: rx.Component,
    **props: object,
) -> rx.Component:
    """Flex row for responsive layouts.

    Args:
        children: Child components.
        **props: Additional Reflex flex props.

    """
    return rx.flex(*children, **{"direction": "row", "align": "center", **props})


def flex_col(
    *children: rx.Component,
    **props: object,
) -> rx.Component:
    """Flex column for responsive layouts.

    Args:
        children: Child components.
        **props: Additional Reflex flex props.

    """
    return rx.flex(*children, **{"direction": "column", **props})


def spacer(**props: object) -> rx.Component:
    """Flexible spacer that pushes elements apart.

    Args:
        **props: Additional Reflex spacer props.

    """
    return rx.spacer(**props)


def divider(**props: object) -> rx.Component:
    """Horizontal divider line.

    Args:
        **props: Additional Reflex box props.

    """
    return rx.box(**{"height": "1px", "width": "100%", "background": DIVIDER, **props})


def divider_vertical(**props: object) -> rx.Component:
    """Vertical divider line.

    Args:
        **props: Additional Reflex box props.

    """
    return rx.box(**{"width": "1px", "height": "100%", "background": DIVIDER, **props})


def scroll_area_v(
    *children: rx.Component,
    height: str = "20rem",
    **props: object,
) -> rx.Component:
    """Vertical scroll area with consistent defaults.

    Args:
        children: Child components.
        height: Scroll area height.
        **props: Additional Reflex scroll_area props.

    """
    return rx.scroll_area(
        *children,
        **{
            "scrollbars": "vertical",
            "type": "hover",
            "height": height,
            "max_height": height,
            **props,
        },
    )


def scroll_area_h(
    *children: rx.Component,
    **props: object,
) -> rx.Component:
    """Horizontal scroll area with consistent defaults.

    Args:
        children: Child components.
        **props: Additional Reflex scroll_area props.

    """
    return rx.scroll_area(
        *children,
        **{"scrollbars": "horizontal", "type": "hover", **props},
    )


def scroll_area_both(
    *children: rx.Component,
    height: str = "20rem",
    width: str = "100%",
    **props: object,
) -> rx.Component:
    """Scroll area with both scrollbars.

    Args:
        children: Child components.
        height: Scroll area height.
        width: Scroll area width.
        **props: Additional Reflex scroll_area props.

    """
    return rx.scroll_area(
        *children,
        **{"scrollbars": "both", "height": height, "width": width, **props},
    )


def grid_cols(
    *children: rx.Component,
    columns: str = "3",
    gap: str = "0.75rem",
    **props: object,
) -> rx.Component:
    """Grid layout with consistent defaults.

    Args:
        children: Child components.
        columns: Number of columns (CSS grid value).
        gap: Grid gap.
        **props: Additional Reflex grid props.

    """
    return rx.grid(
        *children,
        **{"columns": columns, "gap": gap, **props},
    )


def centered_container(
    *children: rx.Component,
    **props: object,
) -> rx.Component:
    """Centered content container.

    Args:
        children: Child components.
        **props: Additional Reflex box props.

    """
    return rx.center(
        *children,
        **{"width": "100%", **props},
    )


def absolute_fill(
    *children: rx.Component,
    **props: object,
) -> rx.Component:
    """Absolutely positioned box that fills its parent.

    Args:
        children: Child components.
        **props: Additional Reflex box props.

    """
    return rx.box(
        *children,
        **{"position": "absolute", "inset": "0", **props},
    )


def page_container(
    *children: rx.Component,
    **props: object,
) -> rx.Component:
    """Create a standard page content container with 86vw max-width.

    Args:
        children: Page content.
        **props: Additional Reflex box props.

    """
    return rx.box(
        *children,
        **{
            "width": HOME_CONTENT_WIDTH,
            "max_width": HOME_CONTENT_MAX_WIDTH,
            "margin": "0 auto",
            **props,
        },
    )


def toolbar_row(
    *children: rx.Component,
    **props: object,
) -> rx.Component:
    """Toolbar row with consistent styling.

    Args:
        children: Toolbar content.
        **props: Additional Reflex box props.

    """
    return rx.box(
        *children,
        **{
            "position": "relative",
            "width": "100%",
            "min_height": "2.5rem",
            **props,
        },
    )
