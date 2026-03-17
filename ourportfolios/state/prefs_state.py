"""
Place at: ourportfolios/state/prefs_state.py

Loaded on every authenticated page mount. Other states read from it.
"""

import reflex as rx
from ..auth_config import get_supabase, AUTH_AVAILABLE


class PrefsState(rx.State):
    experience_level: str = "Beginner"
    default_chart_period: str = "1M"

    # ── Load from Supabase ────────────────────────────────────────────────────

    @rx.event
    async def load(self):
        """Call this in on_load alongside any page-specific loader."""
        from .auth_state import AuthState

        auth = await self.get_state(AuthState)
        if not auth.is_authenticated or not AUTH_AVAILABLE:
            return

        try:
            supabase = get_supabase()
            result = supabase.auth.get_user(auth.auth_token)
            if result.user is None:
                return
            meta = result.user.user_metadata or {}
            self.experience_level = meta.get("experience_level", "Beginner")
            self.default_chart_period = meta.get("default_chart_period", "1M")
        except Exception:
            pass

    # ── Apply to HeatmapState (call from market_overview on_mount) ────────────

    @rx.event
    async def apply_to_heatmap(self):
        from ..state.heatmap import HeatmapState

        heatmap = await self.get_state(HeatmapState)
        heatmap.selected_period = self.default_chart_period
