"""Global framework state management for cross-page framework selection."""

import reflex as rx
from typing import Dict, List, Optional
from sqlalchemy import text
from ..utils.database.database import CompanySession


class GlobalFrameworkState(rx.State):
    """Global state for managing selected investment framework across the application."""

    # Currently selected framework
    selected_framework_id: Optional[int] = None
    selected_framework: Dict = {}

    # Framework metrics mapping
    framework_metrics: Dict[str, List[str]] = {}

    @rx.event
    async def select_framework(self, framework_id: int):
        """Select a framework and load its associated metrics."""
        self.selected_framework_id = framework_id

        # Load framework details
        try:
            async with CompanySession.begin() as session:
                query = text(
                    "SELECT * FROM frameworks.frameworks_df WHERE id = :framework_id"
                )
                result = await session.execute(query, {"framework_id": framework_id})
                framework_data = result.mappings().all()

                if framework_data:
                    self.selected_framework = dict(framework_data[0])
                    await self.load_framework_metrics()
        except Exception as e:
            print(f"Error loading framework: {e}")
            self.selected_framework = {}

    @rx.event
    async def load_framework_metrics(self):
        if not self.selected_framework_id:
            return

        try:
            async with CompanySession.begin() as session:
                query = text("""
                    SELECT category, metrics, display_order
                    FROM frameworks.framework_metrics_df
                    WHERE framework_id = :framework_id
                    ORDER BY display_order
                """)
                result = await session.execute(
                    query, {"framework_id": self.selected_framework_id}
                )
                metrics_data = result.mappings().all()

                # Aggregate metrics by category
                self.framework_metrics = {}
                for row in metrics_data:
                    category = row["category"]
                    metrics = row["metrics"]  # This is already an array from the DB

                    # Initialize category if not exists
                    if category not in self.framework_metrics:
                        self.framework_metrics[category] = []

                    # Metrics is an array, so extend our list with it
                    if isinstance(metrics, list):
                        self.framework_metrics[category].extend(metrics)
                    else:
                        # Fallback if it's a single value
                        self.framework_metrics[category].append(metrics)
        except Exception as e:
            print(f"Error loading framework metrics: {e}")
            self.framework_metrics = {}

    @rx.var
    def has_selected_framework(self) -> bool:
        """Check if a framework is currently selected."""
        return self.selected_framework_id is not None

    @rx.var
    def framework_display_name(self) -> str:
        """Get display name of selected framework."""
        if self.selected_framework:
            return self.selected_framework.get("title", "Unknown Framework")
        return "No Framework Selected"

    @rx.event
    def clear_framework_selection(self):
        """Clear the current framework selection."""
        self.selected_framework_id = None
        self.selected_framework = {}
        self.framework_metrics = {}
