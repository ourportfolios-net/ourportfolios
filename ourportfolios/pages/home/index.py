import reflex as rx
from ...utils.session_manager import SessionIsolatedStateMixin
from ...components.navbar import navbar
from ...components.cards import glass_card


class HomeState(SessionIsolatedStateMixin, rx.State):
    """Homepage state."""

    # Ticker search input
    ticker_search: str = ""

    # Mock market data (in a real app, this would come from an API)
    sp500_value: str = "4,783.45"
    sp500_change: str = "+1.24%"
    nasdaq_value: str = "14,972.76"
    nasdaq_change: str = "+0.75%"
    gold_value: str = "2,018.30"
    gold_change: str = "-0.12%"
    oil_value: str = "71.45"
    oil_change: str = "+0.44%"

    portfolio_value: str = "$142,590.22"
    portfolio_change: str = "+4.8%"

    # Framework stats
    frameworks_count: str = "12"

    # Comparison stats
    active_comparisons: str = "3"

    def on_mount(self):
        super().on_mount()

    def on_unmount(self):
        super().on_unmount()

    def handle_analyze_ticker(self):
        """Navigate to analyze page with the ticker."""
        if self.ticker_search:
            return rx.redirect(f"/analyze?ticker={self.ticker_search}")

    def handle_compare(self):
        """Navigate to compare page."""
        return rx.redirect("/compare")

    def handle_portfolio(self):
        """Navigate to portfolio/select page."""
        return rx.redirect("/select")


def sector_heatmap_cell(name: str, change: str, is_positive: bool = True):
    """Create a sector heatmap cell."""
    color = "emerald" if is_positive else "rose"
    opacity = "10" if abs(float(change.strip("%"))) > 1 else "5"

    return rx.box(
        rx.vstack(
            rx.text(
                name,
                font_size="10px",
                font_weight="700",
                text_transform="uppercase",
                color=f"var(--{color}-9)" if is_positive else f"var(--{color}-9)",
                opacity="0.7",
            ),
            rx.text(
                change,
                font_size="16px",
                font_weight="700",
                color=f"var(--{color}-9)",
            ),
            spacing="1",
            align="start",
        ),
        padding="1rem",
        border_radius="12px",
        background=f"color-mix(in srgb, var(--{color}-9) {opacity}%, transparent)",
        border=f"1px solid color-mix(in srgb, var(--{color}-9) 20%, transparent)",
        min_width="120px",
        flex="1",
        transition="transform 0.2s ease",
        _hover={"transform": "scale(1.05)", "z_index": "10"},
    )


def market_overview_section():
    """Create the market overview section."""
    return glass_card(
        rx.vstack(
            # S&P 500 Index Section - at the top
            rx.hstack(
                rx.hstack(
                    rx.icon("bar-chart-3", size=20),
                    rx.heading(
                        "Market Overview",
                        size="4",
                        font_weight="700",
                    ),
                    spacing="2",
                ),
                rx.spacer(),
                rx.hstack(
                    rx.vstack(
                        rx.text(
                            "S&P 500 INDEX",
                            font_size="10px",
                            font_weight="700",
                            text_transform="uppercase",
                            letter_spacing="0.1em",
                            color="rgba(255, 255, 255, 0.4)",
                        ),
                        rx.hstack(
                            rx.text(
                                HomeState.sp500_value,
                                font_size="24px",
                                font_weight="800",
                            ),
                            rx.badge(
                                HomeState.sp500_change,
                                color_scheme="green",
                                size="1",
                                font_weight="700",
                            ),
                            spacing="2",
                            align="center",
                        ),
                        spacing="1",
                        align="start",
                    ),
                    rx.box(
                        rx.html(
                            """
                            <svg style="width: 100%; height: 100%;" preserveAspectRatio="none" viewBox="0 0 100 40">
                                <path d="M0 35 Q 10 30, 20 5, 30 15, 40 25 T 60 10 T 80 20 T 100 15" 
                                      fill="none" stroke="#8B5CF6" stroke-linecap="round" stroke-width="2.5"/>
                            </svg>
                            """
                        ),
                        width="100px",
                        height="32px",
                    ),
                    spacing="4",
                ),
                width="100%",
                align="center",
                margin_bottom="1rem",
            ),
            # Placeholder for heatmap (large area in middle)
            rx.box(
                rx.text(
                    "Heatmap will be rendered here",
                    font_size="14px",
                    color="rgba(255, 255, 255, 0.3)",
                    font_style="italic",
                ),
                width="100%",
                height="450px",
                padding="2rem",
                border="1px dashed rgba(255, 255, 255, 0.1)",
                border_radius="8px",
                display="flex",
                align_items="center",
                justify_content="center",
                margin_bottom="1rem",
            ),
            # View Full Market link at the bottom
            rx.link(
                rx.hstack(
                    rx.text(
                        "VIEW FULL MARKET",
                        font_size="10px",
                        font_weight="600",
                        letter_spacing="0.1em",
                        color="rgba(255, 255, 255, 0.4)",
                    ),
                    rx.icon("chevron-right", size=14, color="rgba(255, 255, 255, 0.4)"),
                    spacing="1",
                    justify="end",
                    width="100%",
                ),
                href="/compare",
                text_decoration="none",
                _hover={
                    "& p": {"color": "rgba(255, 255, 255, 0.7)"},
                },
            ),
            spacing="3",
            width="100%",
        ),
        padding="1.5rem",
        width="100%",
    )


def decision_hub_card(
    title: str,
    description: str,
    icon: str,
    color: str,
    button_text: str,
    button_variant: str,
    on_click,
    has_input: bool = False,
    has_progress: bool = False,
    has_portfolio_value: bool = False,
    has_framework_count: bool = False,
    has_comparison_count: bool = False,
):
    """Create a decision hub card."""
    blur_color = {
        "purple": "rgba(139, 92, 246, 0.1)",
        "blue": "rgba(59, 130, 246, 0.1)",
        "emerald": "rgba(16, 185, 129, 0.1)",
    }

    hover_blur = {
        "purple": "rgba(139, 92, 246, 0.2)",
        "blue": "rgba(59, 130, 246, 0.2)",
        "emerald": "rgba(16, 185, 129, 0.2)",
    }

    icon_bg = {
        "purple": "rgba(139, 92, 246, 0.2)",
        "blue": "rgba(59, 130, 246, 0.2)",
        "emerald": "rgba(16, 185, 129, 0.2)",
    }

    icon_border = {
        "purple": "rgba(139, 92, 246, 0.3)",
        "blue": "rgba(59, 130, 246, 0.3)",
        "emerald": "rgba(16, 185, 129, 0.3)",
    }

    icon_color = {
        "purple": "var(--accent-purple)",
        "blue": "var(--blue-9)",
        "emerald": "var(--green-9)",
    }

    return rx.box(
        # Blur background effect
        rx.box(
            position="absolute",
            right="-3rem",
            top="-3rem",
            width="160px",
            height="160px",
            background=blur_color.get(color, blur_color["purple"]),
            filter="blur(60px)",
            border_radius="9999px",
            transition="all 0.3s ease",
        ),
        # Content
        glass_card(
            rx.vstack(
                rx.vstack(
                    # Icon
                    rx.box(
                        rx.icon(
                            icon,
                            size=24,
                            color=icon_color.get(color, icon_color["purple"]),
                        ),
                        width="48px",
                        height="48px",
                        border_radius="12px",
                        background=icon_bg.get(color, icon_bg["purple"]),
                        border=f"1px solid {icon_border.get(color, icon_border['purple'])}",
                        display="flex",
                        align_items="center",
                        justify_content="center",
                    ),
                    # Title
                    rx.heading(
                        title,
                        size="6",
                        font_weight="700",
                    ),
                    # Description
                    rx.text(
                        description,
                        color="rgba(255, 255, 255, 0.5)",
                        font_size="14px",
                        line_height="1.6",
                    ),
                    # Optional input field
                    rx.cond(
                        has_input,
                        rx.box(
                            rx.input(
                                placeholder="Enter symbol (e.g. NVDA)",
                                value=HomeState.ticker_search,
                                on_change=HomeState.set_ticker_search,
                                size="3",
                                width="100%",
                                background="rgba(255, 255, 255, 0.05)",
                                border="1px solid rgba(255, 255, 255, 0.1)",
                                border_radius="12px",
                                _focus={
                                    "outline": "none",
                                    "ring": "1px",
                                    "ring_color": "var(--accent-purple)",
                                    "border_color": "var(--accent-purple)",
                                },
                            ),
                            position="relative",
                            width="100%",
                        ),
                    ),
                    # Optional progress bars
                    rx.cond(
                        has_progress,
                        rx.hstack(
                            rx.box(
                                height="6px",
                                flex="1",
                                background="var(--accent-purple)",
                                border_radius="9999px",
                            ),
                            rx.box(
                                height="6px",
                                flex="1",
                                background="var(--blue-9)",
                                border_radius="9999px",
                                opacity="0.5",
                            ),
                            rx.box(
                                height="6px",
                                flex="1",
                                background="rgba(255, 255, 255, 0.1)",
                                border_radius="9999px",
                            ),
                            spacing="2",
                            width="100%",
                        ),
                    ),
                    # Optional portfolio value
                    rx.cond(
                        has_portfolio_value,
                        rx.box(
                            rx.vstack(
                                rx.hstack(
                                    rx.text(
                                        "TOTAL VALUE",
                                        font_size="10px",
                                        font_weight="700",
                                        text_transform="uppercase",
                                        letter_spacing="0.15em",
                                        color="rgba(255, 255, 255, 0.3)",
                                    ),
                                    rx.badge(
                                        HomeState.portfolio_change,
                                        color_scheme="green",
                                        size="1",
                                        font_weight="700",
                                    ),
                                    justify="between",
                                    width="100%",
                                ),
                                rx.text(
                                    HomeState.portfolio_value,
                                    font_size="20px",
                                    font_weight="700",
                                ),
                                spacing="1",
                                align="start",
                            ),
                            padding="1rem",
                            border_radius="12px",
                            background="rgba(255, 255, 255, 0.05)",
                            border="1px solid rgba(255, 255, 255, 0.05)",
                            width="100%",
                        ),
                    ),
                    # Optional framework count
                    rx.cond(
                        has_framework_count,
                        rx.box(
                            rx.vstack(
                                rx.text(
                                    "AVAILABLE FRAMEWORKS",
                                    font_size="10px",
                                    font_weight="700",
                                    text_transform="uppercase",
                                    letter_spacing="0.15em",
                                    color="rgba(255, 255, 255, 0.3)",
                                ),
                                rx.hstack(
                                    rx.text(
                                        HomeState.frameworks_count,
                                        font_size="28px",
                                        font_weight="700",
                                    ),
                                    rx.text(
                                        "frameworks",
                                        font_size="14px",
                                        color="rgba(255, 255, 255, 0.5)",
                                    ),
                                    spacing="2",
                                    align="baseline",
                                ),
                                spacing="1",
                                align="start",
                            ),
                            padding="1rem",
                            border_radius="12px",
                            background="rgba(255, 255, 255, 0.05)",
                            border="1px solid rgba(255, 255, 255, 0.05)",
                            width="100%",
                        ),
                    ),
                    # Optional comparison count
                    rx.cond(
                        has_comparison_count,
                        rx.box(
                            rx.vstack(
                                rx.text(
                                    "ACTIVE COMPARISONS",
                                    font_size="10px",
                                    font_weight="700",
                                    text_transform="uppercase",
                                    letter_spacing="0.15em",
                                    color="rgba(255, 255, 255, 0.3)",
                                ),
                                rx.hstack(
                                    rx.text(
                                        HomeState.active_comparisons,
                                        font_size="28px",
                                        font_weight="700",
                                    ),
                                    rx.text(
                                        "in progress",
                                        font_size="14px",
                                        color="rgba(255, 255, 255, 0.5)",
                                    ),
                                    spacing="2",
                                    align="baseline",
                                ),
                                spacing="1",
                                align="start",
                            ),
                            padding="1rem",
                            border_radius="12px",
                            background="rgba(255, 255, 255, 0.05)",
                            border="1px solid rgba(255, 255, 255, 0.05)",
                            width="100%",
                        ),
                    ),
                    spacing="5",
                    align="start",
                    flex="1",
                ),
                # Button
                rx.button(
                    button_text,
                    size="3",
                    width="100%",
                    font_weight="700",
                    border_radius="12px",
                    variant=button_variant,
                    on_click=on_click,
                    cursor="pointer",
                    transition="all 0.2s ease",
                    _active={"transform": "scale(0.98)"},
                ),
                spacing="4",
                align="start",
                justify="between",
                height="100%",
                width="100%",
            ),
            padding="1.5rem",
            width="100%",
        ),
        position="relative",
        overflow="hidden",
        transition="all 0.3s ease",
        _hover={
            "& > :nth-child(2)": {
                "background": "rgba(255, 255, 255, 0.05)",
                "border_color": "rgba(255, 255, 255, 0.05)",
            }
        },
    )


def decision_hub_section():
    """Create the decision hub section."""
    return rx.vstack(
        # Section Header
        rx.vstack(
            rx.heading(
                "Decision Hub",
                size="8",
                font_weight="800",
                letter_spacing="-0.02em",
            ),
            rx.text(
                "Select a primary workflow to begin your market analysis.",
                color="rgba(255, 255, 255, 0.4)",
                font_weight="500",
            ),
            spacing="2",
            align="start",
        ),
        # Cards Grid - 3 columns on large screens, responsive on smaller
        rx.grid(
            decision_hub_card(
                title="Select Framework",
                description="Choose an investment framework or screening methodology to guide your portfolio construction strategy.",
                icon="layers",
                color="purple",
                button_text="Browse Frameworks",
                button_variant="solid",
                on_click=rx.redirect("/recommend"),
                has_input=False,
                has_framework_count=True,
            ),
            decision_hub_card(
                title="Compare Assets",
                description="Side-by-side performance benchmarking and correlation analysis between multiple tickers or indices.",
                icon="git-compare",
                color="blue",
                button_text="Start Comparison",
                button_variant="outline",
                on_click=HomeState.handle_compare,
                has_progress=False,
                has_comparison_count=True,
            ),
            decision_hub_card(
                title="Manage Portfolio",
                description="Track your personal holdings, monitor risk exposure, and rebalance based on your strategy goals.",
                icon="wallet",
                color="emerald",
                button_text="Open Portfolio Manager",
                button_variant="outline",
                on_click=HomeState.handle_portfolio,
                has_portfolio_value=True,
            ),
            columns=rx.breakpoints(initial="1", md="2", lg="3"),
            gap="1.25rem",
            width="100%",
        ),
        spacing="6",
        width="100%",
        align="start",
    )


def footer_section():
    """Create the footer section."""
    return rx.hstack(
        rx.hstack(
            rx.box(
                width="8px",
                height="8px",
                border_radius="9999px",
                background="var(--green-9)",
                animation="pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite",
            ),
            rx.text(
                "Market Open • Live Data",
                font_size="11px",
                font_weight="700",
                text_transform="uppercase",
                letter_spacing="0.15em",
            ),
            spacing="2",
            align="center",
        ),
        rx.hstack(
            rx.text(
                f"Nasdaq: {HomeState.nasdaq_value} ({HomeState.nasdaq_change})",
                font_size="11px",
                font_weight="700",
                text_transform="uppercase",
                letter_spacing="0.15em",
            ),
            rx.text(
                f"Gold: {HomeState.gold_value} ({HomeState.gold_change})",
                font_size="11px",
                font_weight="700",
                text_transform="uppercase",
                letter_spacing="0.15em",
            ),
            rx.text(
                f"Oil: {HomeState.oil_value} ({HomeState.oil_change})",
                font_size="11px",
                font_weight="700",
                text_transform="uppercase",
                letter_spacing="0.15em",
            ),
            spacing="6",
            wrap="wrap",
        ),
        rx.text(
            "Last Updated: Jan 24, 15:42 UTC",
            font_size="11px",
            font_weight="700",
            text_transform="uppercase",
            letter_spacing="0.15em",
        ),
        justify="between",
        wrap="wrap",
        gap="2.5rem",
        padding_top="2.5rem",
        opacity="0.4",
        width="100%",
    )


@rx.page(route="/home", on_load=HomeState.on_mount)
def index() -> rx.Component:
    """Render the home page."""
    return rx.box(
        navbar(),
        rx.box(
            rx.flex(
                # Decision Hub on the left
                rx.box(
                    decision_hub_section(),
                    flex="1",
                ),
                # Market Overview on the right (40% smaller horizontally)
                rx.box(
                    market_overview_section(),
                    width="32%",
                ),
                direction=rx.breakpoints(initial="column", lg="row"),
                gap="1.5rem",
                width="100%",
                max_width="1440px",
                margin="0 auto",
                align_items="flex-end",
            ),
            padding_x=["1.5rem", "2rem", "3rem"],
            padding_y="2rem",
        ),
        on_unmount=HomeState.on_unmount,
        background="#090909",
        background_image="""
            radial-gradient(circle at 20% 20%, rgba(139, 92, 246, 0.05) 0%, transparent 40%),
            radial-gradient(circle at 80% 80%, rgba(139, 92, 246, 0.03) 0%, transparent 40%)
        """,
        color="white",
        min_height="100vh",
        width="100%",
        overflow_x="hidden",
    )
