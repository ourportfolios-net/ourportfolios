"""
Place at: ourportfolios/state/prefs_state.py
"""

import reflex as rx
from ..auth_config import get_supabase, AUTH_AVAILABLE

_DEFAULT_PERIOD = "1D"


class PrefsState(rx.State):
    experience_level: str = "Beginner"
    default_chart_period: str = _DEFAULT_PERIOD
    _pref_explicitly_set: bool = False

    @rx.event
    async def load(self):
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
            if "default_chart_period" in meta:
                self.default_chart_period = meta["default_chart_period"]
                self._pref_explicitly_set = True
            self.experience_level = meta.get("experience_level", "Beginner")
        except Exception:
            pass

    @rx.event
    async def apply_to_heatmap(self):
        from .auth_state import AuthState
        from ..state.heatmap import HeatmapState
        from ..state.home_state import HomeState

        auth = await self.get_state(AuthState)
        if auth.is_authenticated and AUTH_AVAILABLE:
            await self.load()

        period = (
            self.default_chart_period if self._pref_explicitly_set else _DEFAULT_PERIOD
        )

        heatmap = await self.get_state(HeatmapState)
        heatmap.selected_period = period

        return [
            HeatmapState.load_heatmap_data,
            HomeState.load_ticker_for_period(period),
        ]
