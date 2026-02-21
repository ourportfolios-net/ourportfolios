"""Global framework state management."""

import reflex as rx
from typing import Any, Optional
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from ..utils.database.database import get_company_session
from ..utils.database.models import FrameworkORM, FrameworkMetricsORM


class GlobalFrameworkState(rx.State):
    selected_framework_id: Optional[int] = None
    selected_framework: dict[str, Any] = {}
    framework_metrics: dict[str, list[str]] = {}
    _framework_initialized: bool = False

    @rx.event
    async def select_framework(self, framework_id: int) -> None:
        self.selected_framework_id = framework_id
        self._framework_initialized = False
        try:
            async with get_company_session() as session:
                stmt = (
                    select(FrameworkORM)
                    .options(selectinload(FrameworkORM.metric_rows))
                    .where(FrameworkORM.id == framework_id)
                )
                result = await session.execute(stmt)
                row = result.scalar_one_or_none()
                if row is not None:
                    self.selected_framework = {
                        "id": row.id,
                        "title": row.title,
                        "description": row.description,
                        "author": row.author,
                        "complexity": row.complexity,
                        "scope": row.scope,
                        "industry": row.industry,
                        "source_name": row.source_name,
                        "source_url": row.source_url,
                    }
                    self._build_framework_metrics(row.metric_rows)
                    self._framework_initialized = True
                else:
                    self.selected_framework = {}
        except Exception as e:
            print(f"[select_framework] Error: {e}")
            self.selected_framework = {}

    def _build_framework_metrics(self, metric_rows: list[FrameworkMetricsORM]) -> None:
        metrics: dict[str, list[str]] = {}
        for row in sorted(metric_rows, key=lambda m: m.display_order or 0):
            if row.category not in metrics:
                metrics[row.category] = []
            metrics[row.category].extend(row.metrics)
        self.framework_metrics = metrics

    @rx.event
    async def load_framework_metrics(self) -> None:
        if not self.selected_framework_id:
            return
        try:
            async with get_company_session() as session:
                stmt = (
                    select(FrameworkORM)
                    .options(selectinload(FrameworkORM.metric_rows))
                    .where(FrameworkORM.id == self.selected_framework_id)
                )
                result = await session.execute(stmt)
                row = result.scalar_one_or_none()
                if row is not None:
                    self._build_framework_metrics(row.metric_rows)
        except Exception as e:
            print(f"[load_framework_metrics] Error: {e}")
            self.framework_metrics = {}

    @rx.var
    def has_selected_framework(self) -> bool:
        return self.selected_framework_id is not None

    @rx.var
    def framework_display_name(self) -> str:
        if self.selected_framework:
            return str(self.selected_framework.get("title", "Unknown Framework"))
        return "No Framework Selected"

    @rx.event
    def clear_framework_selection(self) -> None:
        self.selected_framework_id = None
        self.selected_framework = {}
        self.framework_metrics = {}
        self._framework_initialized = False
