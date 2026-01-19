import reflex as rx
import asyncio
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

    # Portfolio values (base and target for animation)
    _base_portfolio_value: float = 142590.22
    _target_portfolio_value: float = 148719.73
    _base_portfolio_change: float = 4.8
    _target_portfolio_change: float = 8.1
    _current_portfolio_value: float = 142590.22
    _current_portfolio_change: float = 4.8
    portfolio_value: str = "$142,590.22"
    portfolio_change: str = "+4.8%"
    is_portfolio_hovered: bool = False
    _animation_running: bool = False

    # Framework card hover state (0 = first selected, 1 = second, 2 = third)
    framework_hover_index: int = 0
    _framework_card_hovered: bool = False
    _framework_cycle_running: bool = False

    # Framework stats
    frameworks_count: str = "12"

    # Comparison stats
    active_comparisons: str = "3"

    # Sample comparison data for the preview chart
    comparison_preview_data: list[dict] = [
        {"period": "Jan", "AAPL": 178, "MSFT": 340},
        {"period": "Feb", "AAPL": 182, "MSFT": 345},
        {"period": "Mar", "AAPL": 175, "MSFT": 352},
        {"period": "Apr", "AAPL": 185, "MSFT": 358},
        {"period": "May", "AAPL": 190, "MSFT": 365},
        {"period": "Jun", "AAPL": 188, "MSFT": 372},
        {"period": "Jul", "AAPL": 195, "MSFT": 380},
        {"period": "Aug", "AAPL": 198, "MSFT": 385},
    ]

    def start_framework_hover(self):
        """Move spotlight to second framework when card is hovered."""
        self._framework_card_hovered = True
        self.framework_hover_index = 1

    def stop_framework_hover(self):
        """Move spotlight back to first framework when mouse leaves."""
        self._framework_card_hovered = False
        self.framework_hover_index = 0

    @rx.event(background=True)
    async def start_portfolio_hover(self):
        """Start the portfolio hover animation with gradual count-up."""
        async with self:
            if self._animation_running:
                return
            self.is_portfolio_hovered = True
            self._animation_running = True

        # Animation parameters - fast and smooth over 0.35s
        duration = 0.35
        steps = 20
        step_duration = duration / steps

        start_value = self._base_portfolio_value
        end_value = self._target_portfolio_value
        start_change = self._base_portfolio_change
        end_change = self._target_portfolio_change

        for i in range(steps + 1):
            async with self:
                if not self.is_portfolio_hovered:
                    self._animation_running = False
                    return

                # Ease-out quart for extra smooth deceleration
                t = i / steps
                eased_t = 1 - (1 - t) ** 4

                current_val = start_value + (end_value - start_value) * eased_t
                current_chg = start_change + (end_change - start_change) * eased_t

                self._current_portfolio_value = current_val
                self._current_portfolio_change = current_chg
                self.portfolio_value = f"${current_val:,.2f}"
                self.portfolio_change = f"+{current_chg:.1f}%"

            if i < steps:
                await asyncio.sleep(step_duration)

        async with self:
            self._animation_running = False

    @rx.event(background=True)
    async def end_portfolio_hover(self):
        """End the portfolio hover animation with gradual count-down."""
        async with self:
            if self._animation_running and not self.is_portfolio_hovered:
                return
            self.is_portfolio_hovered = False
            self._animation_running = True

        # Animation parameters - fast return over 0.35s
        duration = 0.35
        steps = 20
        step_duration = duration / steps

        async with self:
            start_value = self._current_portfolio_value
            start_change = self._current_portfolio_change
        end_value = self._base_portfolio_value
        end_change = self._base_portfolio_change

        for i in range(steps + 1):
            async with self:
                if self.is_portfolio_hovered:
                    self._animation_running = False
                    return

                # Ease-out quart for extra smooth deceleration
                t = i / steps
                eased_t = 1 - (1 - t) ** 4

                current_val = start_value + (end_value - start_value) * eased_t
                current_chg = start_change + (end_change - start_change) * eased_t

                self._current_portfolio_value = current_val
                self._current_portfolio_change = current_chg
                self.portfolio_value = f"${current_val:,.2f}"
                self.portfolio_change = f"+{current_chg:.1f}%"

            if i < steps:
                await asyncio.sleep(step_duration)

        async with self:
            self._animation_running = False

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
                    rx.icon("bar-chart-3", size=16),
                    rx.heading(
                        "Market Overview",
                        size="3",
                        font_weight="700",
                    ),
                    spacing="2",
                ),
                rx.spacer(),
                rx.hstack(
                    rx.vstack(
                        rx.text(
                            "S&P 500 INDEX",
                            font_size="8px",
                            font_weight="700",
                            text_transform="uppercase",
                            letter_spacing="0.1em",
                            color="rgba(255, 255, 255, 0.4)",
                        ),
                        rx.hstack(
                            rx.text(
                                HomeState.sp500_value,
                                font_size="18px",
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
                        width="80px",
                        height="24px",
                    ),
                    spacing="3",
                ),
                width="100%",
                align="center",
                margin_bottom="0.75rem",
            ),
            # Placeholder for heatmap (large area in middle)
            rx.box(
                rx.text(
                    "Heatmap will be rendered here",
                    font_size="12px",
                    color="rgba(255, 255, 255, 0.3)",
                    font_style="italic",
                ),
                width="100%",
                height="500px",
                padding="1.5rem",
                border="1px dashed rgba(255, 255, 255, 0.1)",
                border_radius="12px",
                display="flex",
                align_items="center",
                justify_content="center",
                margin_bottom="0.75rem",
            ),
            # View Full Market link at the bottom
            rx.link(
                rx.hstack(
                    rx.spacer(),
                    rx.text(
                        "VIEW FULL MARKET",
                        font_size="9px",
                        font_weight="600",
                        letter_spacing="0.1em",
                        color="rgba(255, 255, 255, 0.4)",
                    ),
                    rx.icon("chevron-right", size=12, color="rgba(255, 255, 255, 0.4)"),
                    spacing="1",
                    width="100%",
                ),
                href="/compare",
                text_decoration="none",
                _hover={
                    "& p": {"color": "rgba(255, 255, 255, 0.7)"},
                },
            ),
            spacing="2",
            width="100%",
        ),
        padding="0.75rem",
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
    has_comparison_chart: bool = False,
    has_framework_list: bool = False,
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
                            size=20,
                            color=icon_color.get(color, icon_color["purple"]),
                        ),
                        width="40px",
                        height="40px",
                        border_radius="10px",
                        background=icon_bg.get(color, icon_bg["purple"]),
                        border=f"1px solid {icon_border.get(color, icon_border['purple'])}",
                        display="flex",
                        align_items="center",
                        justify_content="center",
                    ),
                    # Title
                    rx.heading(
                        title,
                        size="5",
                        font_weight="700",
                    ),
                    # Description
                    rx.text(
                        description,
                        color="rgba(255, 255, 255, 0.5)",
                        font_size="12px",
                        line_height="1.5",
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
                                        font_size="8px",
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
                                    font_size="18px",
                                    font_weight="700",
                                ),
                                spacing="1",
                                align="start",
                            ),
                            padding="0.75rem",
                            border_radius="10px",
                            background="rgba(255, 255, 255, 0.03)",
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
                                    font_size="8px",
                                    font_weight="700",
                                    text_transform="uppercase",
                                    letter_spacing="0.15em",
                                    color="rgba(255, 255, 255, 0.3)",
                                ),
                                # Grid of mini framework icons
                                rx.grid(
                                    *[
                                        rx.box(
                                            width="24px",
                                            height="24px",
                                            border_radius="6px",
                                            background="rgba(139, 92, 246, 0.2)",
                                            border="1px solid rgba(139, 92, 246, 0.3)",
                                        )
                                        for _ in range(12)
                                    ],
                                    columns="6",
                                    gap="0.5rem",
                                    width="100%",
                                ),
                                spacing="2",
                                align="start",
                            ),
                            padding="0.75rem",
                            border_radius="10px",
                            background="rgba(255, 255, 255, 0.03)",
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
                                    font_size="8px",
                                    font_weight="700",
                                    text_transform="uppercase",
                                    letter_spacing="0.15em",
                                    color="rgba(255, 255, 255, 0.3)",
                                ),
                                # Visual progress indicators
                                rx.vstack(
                                    # Comparison 1
                                    rx.hstack(
                                        rx.box(
                                            width="8px",
                                            height="8px",
                                            border_radius="9999px",
                                            background="var(--blue-9)",
                                        ),
                                        rx.box(
                                            flex="1",
                                            height="4px",
                                            border_radius="9999px",
                                            background="linear-gradient(to right, var(--blue-9) 60%, rgba(255,255,255,0.1) 60%)",
                                        ),
                                        spacing="2",
                                        width="100%",
                                        align="center",
                                    ),
                                    # Comparison 2
                                    rx.hstack(
                                        rx.box(
                                            width="8px",
                                            height="8px",
                                            border_radius="9999px",
                                            background="var(--blue-9)",
                                        ),
                                        rx.box(
                                            flex="1",
                                            height="4px",
                                            border_radius="9999px",
                                            background="linear-gradient(to right, var(--blue-9) 35%, rgba(255,255,255,0.1) 35%)",
                                        ),
                                        spacing="2",
                                        width="100%",
                                        align="center",
                                    ),
                                    # Comparison 3
                                    rx.hstack(
                                        rx.box(
                                            width="8px",
                                            height="8px",
                                            border_radius="9999px",
                                            background="var(--blue-9)",
                                        ),
                                        rx.box(
                                            flex="1",
                                            height="4px",
                                            border_radius="9999px",
                                            background="linear-gradient(to right, var(--blue-9) 80%, rgba(255,255,255,0.1) 80%)",
                                        ),
                                        spacing="2",
                                        width="100%",
                                        align="center",
                                    ),
                                    spacing="2",
                                    width="100%",
                                ),
                                spacing="2",
                                align="start",
                            ),
                            padding="0.75rem",
                            border_radius="10px",
                            background="rgba(255, 255, 255, 0.03)",
                            border="1px solid rgba(255, 255, 255, 0.05)",
                            width="100%",
                        ),
                    ),
                    # Optional comparison chart (from design)
                    rx.cond(
                        has_comparison_chart,
                        rx.box(
                            rx.vstack(
                                # Ticker badges
                                rx.hstack(
                                    rx.badge(
                                        rx.hstack(
                                            rx.icon("trending-up", size=12),
                                            rx.text(
                                                "AAPL",
                                                font_size="11px",
                                                font_weight="700",
                                            ),
                                            spacing="1",
                                            align="center",
                                        ),
                                        color_scheme="cyan",
                                        variant="soft",
                                        size="2",
                                        border_radius="12px",
                                        padding="0.5rem 0.75rem",
                                    ),
                                    rx.badge(
                                        rx.hstack(
                                            rx.icon("trending-up", size=12),
                                            rx.text(
                                                "MSFT",
                                                font_size="11px",
                                                font_weight="700",
                                            ),
                                            spacing="1",
                                            align="center",
                                        ),
                                        color_scheme="purple",
                                        variant="soft",
                                        size="2",
                                        border_radius="12px",
                                        padding="0.5rem 0.75rem",
                                    ),
                                    spacing="2",
                                    width="100%",
                                ),
                                # Chart visualization using recharts
                                rx.box(
                                    rx.recharts.area_chart(
                                        rx.recharts.area(
                                            data_key="AAPL",
                                            stroke=rx.color("cyan", 9),
                                            fill=rx.color("cyan", 3),
                                            stroke_width=2,
                                            type_="monotone",
                                        ),
                                        rx.recharts.area(
                                            data_key="MSFT",
                                            stroke=rx.color("violet", 9),
                                            fill=rx.color("violet", 3),
                                            stroke_width=2,
                                            type_="monotone",
                                        ),
                                        rx.recharts.x_axis(
                                            data_key="period", hide=True
                                        ),
                                        rx.recharts.y_axis(hide=True),
                                        data=HomeState.comparison_preview_data,
                                        width="100%",
                                        height=100,
                                        margin={
                                            "top": 5,
                                            "right": 5,
                                            "left": 5,
                                            "bottom": 5,
                                        },
                                    ),
                                    width="100%",
                                    height="100px",
                                    position="relative",
                                ),
                                spacing="3",
                                align="start",
                                width="100%",
                            ),
                            padding="1rem",
                            border_radius="12px",
                            background="rgba(255, 255, 255, 0.03)",
                            border="1px solid rgba(255, 255, 255, 0.05)",
                            width="100%",
                        ),
                    ),
                    # Optional framework list (from design)
                    rx.cond(
                        has_framework_list,
                        rx.box(
                            rx.vstack(
                                rx.text(
                                    "AVAILABLE FRAMEWORKS",
                                    font_size="8px",
                                    font_weight="700",
                                    text_transform="uppercase",
                                    letter_spacing="0.15em",
                                    color="rgba(255, 255, 255, 0.3)",
                                    margin_bottom="0.5rem",
                                ),
                                # Framework option 1 (selected)
                                rx.box(
                                    rx.hstack(
                                        rx.box(
                                            rx.icon(
                                                "shield",
                                                size=18,
                                                color="var(--indigo-9)",
                                            ),
                                            width="36px",
                                            height="36px",
                                            border_radius="12px",
                                            background="rgba(99, 102, 241, 0.15)",
                                            border="1px solid rgba(99, 102, 241, 0.3)",
                                            display="flex",
                                            align_items="center",
                                            justify_content="center",
                                        ),
                                        rx.vstack(
                                            rx.text(
                                                "Value Investing",
                                                font_size="13px",
                                                font_weight="700",
                                            ),
                                            rx.text(
                                                "Focuses on undervalued assets with strong fundamentals.",
                                                font_size="11px",
                                                color="rgba(255, 255, 255, 0.5)",
                                                line_height="1.4",
                                            ),
                                            spacing="0",
                                            align="start",
                                            flex="1",
                                        ),
                                        spacing="3",
                                        align="start",
                                        width="100%",
                                    ),
                                    padding="0.75rem",
                                    border_radius="10px",
                                    background="rgba(99, 102, 241, 0.1)",
                                    border="1.5px solid rgba(99, 102, 241, 0.4)",
                                    width="100%",
                                    position="relative",
                                    _before={
                                        "content": '""',
                                        "position": "absolute",
                                        "inset": "-1px",
                                        "border_radius": "10px",
                                        "padding": "1px",
                                        "background": "linear-gradient(135deg, rgba(99, 102, 241, 0.3), transparent)",
                                        "mask": "linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0)",
                                        "mask_composite": "exclude",
                                    },
                                ),
                                # Framework option 2
                                rx.box(
                                    rx.hstack(
                                        rx.box(
                                            rx.icon(
                                                "zap",
                                                size=18,
                                                color="rgba(255, 255, 255, 0.4)",
                                            ),
                                            width="36px",
                                            height="36px",
                                            border_radius="12px",
                                            background="rgba(255, 255, 255, 0.05)",
                                            border="1px solid rgba(255, 255, 255, 0.08)",
                                            display="flex",
                                            align_items="center",
                                            justify_content="center",
                                        ),
                                        rx.vstack(
                                            rx.text(
                                                "Growth Strategy",
                                                font_size="13px",
                                                font_weight="600",
                                                color="rgba(255, 255, 255, 0.7)",
                                            ),
                                            spacing="0",
                                            align="start",
                                            flex="1",
                                        ),
                                        spacing="3",
                                        align="center",
                                        width="100%",
                                    ),
                                    padding="0.75rem",
                                    border_radius="10px",
                                    background="rgba(255, 255, 255, 0.03)",
                                    border="1px solid rgba(255, 255, 255, 0.05)",
                                    width="100%",
                                ),
                                # Framework option 3
                                rx.box(
                                    rx.hstack(
                                        rx.box(
                                            rx.icon(
                                                "compass",
                                                size=18,
                                                color="rgba(255, 255, 255, 0.4)",
                                            ),
                                            width="36px",
                                            height="36px",
                                            border_radius="12px",
                                            background="rgba(255, 255, 255, 0.05)",
                                            border="1px solid rgba(255, 255, 255, 0.08)",
                                            display="flex",
                                            align_items="center",
                                            justify_content="center",
                                        ),
                                        rx.vstack(
                                            rx.text(
                                                "Strategic Allocation",
                                                font_size="13px",
                                                font_weight="600",
                                                color="rgba(255, 255, 255, 0.7)",
                                            ),
                                            spacing="0",
                                            align="start",
                                            flex="1",
                                        ),
                                        spacing="3",
                                        align="center",
                                        width="100%",
                                    ),
                                    padding="0.75rem",
                                    border_radius="10px",
                                    background="rgba(255, 255, 255, 0.03)",
                                    border="1px solid rgba(255, 255, 255, 0.05)",
                                    width="100%",
                                ),
                                spacing="2",
                                align="start",
                                width="100%",
                            ),
                            padding="1rem",
                            border_radius="12px",
                            background="rgba(255, 255, 255, 0.02)",
                            border="1px solid rgba(255, 255, 255, 0.05)",
                            width="100%",
                        ),
                    ),
                    spacing="3",
                    align="start",
                    flex="1",
                ),
                # Button
                rx.button(
                    button_text,
                    size="2",
                    width="100%",
                    font_weight="700",
                    border_radius="10px",
                    variant=button_variant,
                    on_click=on_click,
                    cursor="pointer",
                    transition="all 0.2s ease",
                    _active={"transform": "scale(0.98)"},
                ),
                spacing="3",
                align="start",
                justify="between",
                height="100%",
                width="100%",
            ),
            padding="1rem",
            width="100%",
            min_height="360px",
            transition="background 0.15s ease, border-color 0.15s ease",
        ),
        height="100%",
        position="relative",
        overflow="hidden",
        transition="all 0.3s ease",
        _hover={
            "& > :nth-child(2)": {
                "background": "rgba(255 255, 255, 0.04)",
                "border_color": "rgba(255, 255, 255, 0.05)",
            }
        },
    )


def skeleton_box(width: str, height: str = "12px") -> rx.Component:
    """Create a static skeleton placeholder box."""
    return rx.box(
        width=width,
        height=height,
        border_radius="4px",
        background="rgba(255, 255, 255, 0.08)",
    )


def framework_skeleton_card(icon_name: str, index: int) -> rx.Component:
    """Create a skeleton framework card - hides content when glass is over it."""
    return rx.box(
        rx.hstack(
            # Icon box - dimmed
            rx.box(
                rx.icon(
                    icon_name,
                    size=18,
                    color="rgba(255, 255, 255, 0.3)",
                ),
                width="36px",
                height="36px",
                border_radius="12px",
                background="rgba(255, 255, 255, 0.05)",
                border="1px solid rgba(255, 255, 255, 0.08)",
                display="flex",
                align_items="center",
                justify_content="center",
                # Hide when glass is over this card
                opacity=rx.cond(
                    HomeState.framework_hover_index == index,
                    "0",
                    "1",
                ),
                transition="opacity 0.3s ease",
            ),
            # Skeleton content
            rx.vstack(
                skeleton_box("80%", "13px"),
                rx.vstack(
                    skeleton_box("95%", "8px"),
                    skeleton_box("70%", "8px"),
                    spacing="1",
                    width="100%",
                    margin_top="4px",
                ),
                spacing="1",
                align="start",
                flex="1",
                overflow="hidden",
                # Hide when glass is over this card
                opacity=rx.cond(
                    HomeState.framework_hover_index == index,
                    "0",
                    "1",
                ),
                transition="opacity 0.3s ease",
            ),
            spacing="3",
            align="center",
            width="100%",
        ),
        padding="0.75rem",
        border_radius="10px",
        background="rgba(255, 255, 255, 0.03)",
        border="1px solid rgba(255, 255, 255, 0.05)",
        width="100%",
        height="72px",
    )


def framework_glass_block(
    icon_name: str,
    title: str,
    description: str,
) -> rx.Component:
    """The glass block content that aligns with skeleton cards."""
    return rx.hstack(
        # Icon box - highlighted (matches skeleton icon position)
        rx.box(
            rx.icon(
                icon_name,
                size=18,
                color="var(--indigo-9)",
            ),
            width="36px",
            height="36px",
            border_radius="12px",
            background="rgba(99, 102, 241, 0.15)",
            border="1px solid rgba(99, 102, 241, 0.3)",
            display="flex",
            align_items="center",
            justify_content="center",
            flex_shrink="0",
        ),
        # Content area - matches skeleton text positions
        rx.vstack(
            rx.text(
                title,
                font_size="13px",
                font_weight="700",
                color="white",
                line_height="1",
            ),
            rx.vstack(
                rx.text(
                    description,
                    font_size="11px",
                    color="rgba(255, 255, 255, 0.6)",
                    line_height="1.4",
                ),
                spacing="1",
                width="100%",
                margin_top="4px",
            ),
            spacing="1",
            align="start",
            flex="1",
            overflow="hidden",
        ),
        spacing="3",
        align="center",
        width="100%",
        height="100%",
        padding="0.75rem",
    )


def select_framework_card() -> rx.Component:
    """Create the Select Framework card with glass spotlight effect."""
    # Card height for each mini framework card
    card_height = "72px"

    return rx.box(
        # Blur background effect
        rx.box(
            position="absolute",
            right="-3rem",
            top="-3rem",
            width="160px",
            height="160px",
            background="rgba(139, 92, 246, 0.1)",
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
                            "layers",
                            size=20,
                            color="var(--accent-purple)",
                        ),
                        width="40px",
                        height="40px",
                        border_radius="12px",
                        background="rgba(139, 92, 246, 0.2)",
                        border="1px solid rgba(139, 92, 246, 0.3)",
                        display="flex",
                        align_items="center",
                        justify_content="center",
                    ),
                    # Title
                    rx.heading(
                        "Select Framework",
                        size="5",
                        font_weight="700",
                    ),
                    # Description
                    rx.text(
                        "Choose an investment framework or screening methodology to guide your portfolio construction strategy.",
                        color="rgba(255, 255, 255, 0.5)",
                        font_size="12px",
                        line_height="1.5",
                    ),
                    # Framework list with glass spotlight
                    rx.box(
                        rx.vstack(
                            rx.text(
                                "AVAILABLE FRAMEWORKS",
                                font_size="8px",
                                font_weight="700",
                                text_transform="uppercase",
                                letter_spacing="0.15em",
                                color="rgba(255, 255, 255, 0.3)",
                                margin_bottom="0.5rem",
                            ),
                            # Container for the cards with glass spotlight overlay
                            rx.box(
                                # Base layer: skeleton cards (hide content when glass is over)
                                rx.vstack(
                                    framework_skeleton_card(
                                        icon_name="shield", index=0
                                    ),
                                    framework_skeleton_card(icon_name="zap", index=1),
                                    spacing="2",
                                    align="start",
                                    width="100%",
                                ),
                                # Glass block - acts as a window that reveals content
                                rx.box(
                                    # Content layer - moves opposite to glass to stay in place
                                    rx.box(
                                        # First card content (Value Investing)
                                        rx.box(
                                            framework_glass_block(
                                                icon_name="shield",
                                                title="Value Investing",
                                                description="Focuses on undervalued assets with strong fundamentals.",
                                            ),
                                            position="absolute",
                                            top="0",
                                            left="0",
                                            right="0",
                                            height=card_height,
                                        ),
                                        # Second card content (Growth Strategy)
                                        rx.box(
                                            framework_glass_block(
                                                icon_name="zap",
                                                title="Growth Strategy",
                                                description="Targets high-growth companies with expanding market share.",
                                            ),
                                            position="absolute",
                                            top=f"calc({card_height} + 8px)",
                                            left="0",
                                            right="0",
                                            height=card_height,
                                        ),
                                        position="absolute",
                                        # Move opposite to glass position to create reveal effect
                                        top=rx.cond(
                                            HomeState.framework_hover_index == 0,
                                            "0",
                                            f"calc(-{card_height} - 8px)",
                                        ),
                                        left="0",
                                        right="0",
                                        height=f"calc({card_height} * 2 + 8px)",
                                        transition="top 0.4s cubic-bezier(0.4, 0, 0.2, 1)",
                                    ),
                                    position="absolute",
                                    top=rx.cond(
                                        HomeState.framework_hover_index == 0,
                                        "0",
                                        f"calc({card_height} + 8px)",
                                    ),
                                    left="0",
                                    right="0",
                                    height=card_height,
                                    background="linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(99, 102, 241, 0.04) 100%)",
                                    backdrop_filter="blur(8px)",
                                    border_radius="10px",
                                    border="1.5px solid rgba(99, 102, 241, 0.4)",
                                    box_shadow="0 4px 20px rgba(99, 102, 241, 0.15), inset 0 1px 1px rgba(255, 255, 255, 0.1)",
                                    overflow="hidden",
                                    transition="top 0.4s cubic-bezier(0.4, 0, 0.2, 1)",
                                    pointer_events="none",
                                ),
                                position="relative",
                                width="100%",
                                height=f"calc({card_height} * 2 + 8px)",
                            ),
                            spacing="2",
                            align="start",
                            width="100%",
                        ),
                        padding="1rem",
                        border_radius="12px",
                        background="rgba(255, 255, 255, 0.02)",
                        border="1px solid rgba(255, 255, 255, 0.05)",
                        width="100%",
                    ),
                    spacing="3",
                    align="start",
                    flex="1",
                ),
                # Button
                rx.button(
                    "Browse Frameworks",
                    size="2",
                    width="100%",
                    font_weight="700",
                    border_radius="10px",
                    variant="solid",
                    on_click=rx.redirect("/recommend"),
                    cursor="pointer",
                    transition="all 0.2s ease",
                    _active={"transform": "scale(0.98)"},
                ),
                spacing="3",
                align="start",
                justify="between",
                height="100%",
                width="100%",
            ),
            padding="1rem",
            width="100%",
            min_height="360px",
            transition="background 0.15s ease, border-color 0.15s ease",
        ),
        height="100%",
        position="relative",
        overflow="hidden",
        transition="all 0.3s ease",
        # Card-level hover moves block to second, leave returns to first
        on_mouse_enter=HomeState.start_framework_hover,
        on_mouse_leave=HomeState.stop_framework_hover,
        _hover={
            "& > :nth-child(2)": {
                "background": "rgba(255, 255, 255, 0.04)",
                "border_color": "rgba(255, 255, 255, 0.05)",
            }
        },
    )


def portfolio_card_with_hover():
    """Create the portfolio card with hover animation for values."""
    return rx.box(
        # Blur background effect
        rx.box(
            position="absolute",
            right="-3rem",
            top="-3rem",
            width="160px",
            height="160px",
            background="rgba(16, 185, 129, 0.1)",
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
                            "wallet",
                            size=20,
                            color="var(--green-9)",
                        ),
                        width="40px",
                        height="40px",
                        border_radius="10px",
                        background="rgba(16, 185, 129, 0.2)",
                        border="1px solid rgba(16, 185, 129, 0.3)",
                        display="flex",
                        align_items="center",
                        justify_content="center",
                    ),
                    # Title
                    rx.heading(
                        "Manage Portfolio",
                        size="5",
                        font_weight="700",
                    ),
                    # Description
                    rx.text(
                        "Track your personal holdings, monitor risk exposure, and rebalance based on your strategy goals.",
                        color="rgba(255, 255, 255, 0.5)",
                        font_size="12px",
                        line_height="1.5",
                    ),
                    # Portfolio value with animated values
                    rx.box(
                        rx.vstack(
                            rx.hstack(
                                rx.text(
                                    "TOTAL VALUE",
                                    font_size="8px",
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
                                    style={
                                        "transition": "all 1s ease",
                                    },
                                ),
                                justify="between",
                                width="100%",
                            ),
                            rx.text(
                                HomeState.portfolio_value,
                                font_size="18px",
                                font_weight="700",
                                style={
                                    "transition": "all 1s ease",
                                },
                            ),
                            spacing="1",
                            align="start",
                        ),
                        padding="0.75rem",
                        border_radius="10px",
                        background="rgba(255, 255, 255, 0.03)",
                        border="1px solid rgba(255, 255, 255, 0.05)",
                        width="100%",
                    ),
                    spacing="3",
                    align="start",
                    flex="1",
                ),
                # Button
                rx.button(
                    "Open Portfolio Manager",
                    size="2",
                    width="100%",
                    font_weight="700",
                    border_radius="10px",
                    variant="outline",
                    on_click=HomeState.handle_portfolio,
                    cursor="pointer",
                    transition="all 0.2s ease",
                    _active={"transform": "scale(0.98)"},
                ),
                spacing="3",
                align="start",
                justify="between",
                height="100%",
                width="100%",
            ),
            padding="1rem",
            width="100%",
            min_height="360px",
            transition="background 0.15s ease, border-color 0.15s ease",
        ),
        height="100%",
        position="relative",
        overflow="hidden",
        transition="all 0.3s ease",
        on_mouse_enter=HomeState.start_portfolio_hover,
        on_mouse_leave=HomeState.end_portfolio_hover,
        _hover={
            "& > :nth-child(2)": {
                "background": "rgba(255, 255, 255, 0.04)",
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
            select_framework_card(),
            decision_hub_card(
                title="Compare Assets",
                description="Side-by-side performance benchmarking and correlation analysis between multiple tickers or indices.",
                icon="git-compare",
                color="blue",
                button_text="Start Comparison",
                button_variant="outline",
                on_click=HomeState.handle_compare,
                has_progress=False,
                has_comparison_count=False,
                has_comparison_chart=True,
            ),
            portfolio_card_with_hover(),
            columns=rx.breakpoints(initial="1", md="2", lg="3"),
            gap="1rem",
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
                # Market Overview on the right (slimmer)
                rx.box(
                    market_overview_section(),
                    width="26%",
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
        color="white",
        min_height="100vh",
        width="100%",
        overflow_x="hidden",
    )
