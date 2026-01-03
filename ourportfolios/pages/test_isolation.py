"""Test page to validate session isolation is working correctly.

Navigate to /test-isolation, wait 2 seconds, then click back.
Check terminal logs to confirm API calls were cancelled.
"""

import reflex as rx
import asyncio
from datetime import datetime
from ..utils.session_manager import SessionIsolatedStateMixin, session_isolated


class TestIsolationState(SessionIsolatedStateMixin, rx.State):
    """Test state to validate session isolation."""

    status: str = "Idle"
    start_time: str = ""
    api_call_completed: bool = False
    data: str = ""

    @rx.event
    async def on_mount(self):
        """Initialize test session."""
        super().on_mount()
        print("🧪 TEST: Page mounted, session started")

    @rx.event
    async def on_unmount(self):
        """Cleanup test session."""
        print("🧪 TEST: Page unmounting, cancelling session...")
        await super().on_unmount()
        print("🧪 TEST: Session cancelled")

    @rx.event
    @session_isolated
    async def simulate_slow_api_call(self):
        """Simulate a slow API call that takes 10 seconds."""
        self.status = "Starting API call..."
        self.start_time = datetime.now().strftime("%H:%M:%S")
        self.api_call_completed = False

        print("🧪 TEST: Starting 10-second API call")

        # Simulate slow API call
        for i in range(10):
            await asyncio.sleep(1)

            # Check if still mounted
            if not self.is_mounted():
                print(
                    f"🧪 TEST: API call stopped at {i + 1}/10 seconds (user navigated away)"
                )
                self.status = "CANCELLED at checkpoint"
                return

            self.status = f"API call in progress... {i + 1}/10 seconds"
            print(f"🧪 TEST: API call progress: {i + 1}/10 seconds")

        # If we get here, user stayed on page
        self.api_call_completed = True
        self.status = "API call completed successfully!"
        self.data = "Data loaded at " + datetime.now().strftime("%H:%M:%S")
        print("🧪 TEST: API call completed (user stayed on page)")

    @rx.event
    @session_isolated
    async def simulate_multiple_api_calls(self):
        """Simulate multiple API calls in parallel."""
        self.status = "Starting 3 parallel API calls..."

        async def call_1():
            print("🧪 TEST: API call 1 starting")
            await asyncio.sleep(5)
            print("🧪 TEST: API call 1 completed")
            return "Data 1"

        async def call_2():
            print("🧪 TEST: API call 2 starting")
            await asyncio.sleep(7)
            print("🧪 TEST: API call 2 completed")
            return "Data 2"

        async def call_3():
            print("🧪 TEST: API call 3 starting")
            await asyncio.sleep(3)
            print("🧪 TEST: API call 3 completed")
            return "Data 3"

        # Run all in parallel
        results = await asyncio.gather(call_1(), call_2(), call_3())

        if not self.is_mounted():
            print(
                "🧪 TEST: Parallel calls finished but session cancelled, discarding results"
            )
            return

        self.status = "All API calls completed!"
        self.data = ", ".join(results)
        print("🧪 TEST: All parallel API calls completed successfully")


@rx.page(
    route="/test-isolation",
    on_load=[TestIsolationState.on_mount],
)
def test_isolation():
    """Test page to validate session isolation."""
    return rx.box(
        rx.vstack(
            rx.heading("Session Isolation Test Page", size="8"),
            rx.text(
                "This page tests if API calls are properly cancelled when you navigate away.",
                color="gray",
            ),
            rx.divider(),
            rx.vstack(
                rx.heading("Test 1: Single Slow API Call", size="6"),
                rx.text(
                    "Click 'Start Slow API Call', wait 2-3 seconds, then click 'Go Back'"
                ),
                rx.text(
                    "Check terminal logs - you should see the API call stop at 2-3/10 seconds"
                ),
                rx.hstack(
                    rx.button(
                        "Start Slow API Call (10s)",
                        on_click=TestIsolationState.simulate_slow_api_call,
                        color_scheme="blue",
                    ),
                    rx.link(
                        rx.button("Go Back", color_scheme="red"),
                        href="/",
                    ),
                ),
                rx.text(f"Status: {TestIsolationState.status}", weight="bold"),
                rx.text(f"Started at: {TestIsolationState.start_time}"),
                rx.cond(
                    TestIsolationState.api_call_completed,
                    rx.text("✅ API call completed", color="green"),
                    rx.text("⏳ API call not completed yet", color="orange"),
                ),
                rx.text(f"Data: {TestIsolationState.data}"),
                align_items="flex-start",
                spacing="3",
            ),
            rx.divider(),
            rx.vstack(
                rx.heading("Test 2: Multiple Parallel API Calls", size="6"),
                rx.text(
                    "Click 'Start Parallel Calls', wait 2 seconds, then click 'Go Back'"
                ),
                rx.text("Check terminal logs - all 3 API calls should be cancelled"),
                rx.button(
                    "Start Parallel API Calls",
                    on_click=TestIsolationState.simulate_multiple_api_calls,
                    color_scheme="purple",
                ),
                align_items="flex-start",
                spacing="3",
            ),
            rx.divider(),
            rx.heading("Expected Behavior", size="6"),
            rx.unordered_list(
                rx.list_item(
                    "When you click 'Go Back', API calls should stop immediately"
                ),
                rx.list_item(
                    "Terminal logs should show 'SESSION: Cancelling X running tasks'"
                ),
                rx.list_item("No data updates should occur after navigation"),
                rx.list_item(
                    "Status should show 'CANCELLED at checkpoint' if stopped mid-execution"
                ),
            ),
            spacing="4",
            padding="4",
            max_width="800px",
        ),
        on_unmount=TestIsolationState.on_unmount,
    )
