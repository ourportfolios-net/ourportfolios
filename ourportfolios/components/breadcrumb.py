"""Reusable breadcrumb component that auto-generates from the current route."""

from typing import Optional

import reflex as rx


def _separator() -> rx.Component:
    return rx.icon(
        "chevron-right",
        size=13,
        color="rgba(255,255,255,0.2)",
    )


def _segment_link(label: str, href: str) -> rx.Component:
    return rx.link(
        label,
        href=href,
        size="2",
        color="rgba(255,255,255,0.35)",
        _hover={"color": "white"},
        underline="none",
        transition="color 0.15s ease",
    )


def _active_segment(label: rx.Var[str] | str) -> rx.Component:
    return rx.text(
        label,
        size="2",
        color="rgba(255,255,255,0.75)",
        weight="medium",
    )


def breadcrumb(
    route: str,
    tail_label: Optional[rx.Var[str] | str] = None,
) -> rx.Component:
    """Build a breadcrumb trail from a route string.

    Args:
        route: The page route, e.g. "/tickers" or "/tickers/[ticker]".
        tail_label: If given, replaces the last segment label. Useful for
            dynamic segments like a ticker symbol resolved at runtime.
    """
    parts = [p for p in route.strip("/").split("/") if p]

    children: list[rx.Component] = [
        _segment_link("Home", "/home"),
    ]

    for i, part in enumerate(parts):
        children.append(_separator())
        is_last = i == len(parts) - 1
        href = "/" + "/".join(parts[: i + 1])

        if is_last:
            label = tail_label if tail_label is not None else part.capitalize()
            children.append(_active_segment(label))
        else:
            children.append(_segment_link(part.capitalize(), href))

    return rx.hstack(
        *children,
        spacing="2",
        align="center",
    )
