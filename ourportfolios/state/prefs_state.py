"""State for user preference loading and application."""

import reflex as rx

from ourportfolios.auth_config import AUTH_AVAILABLE, get_supabase
from ourportfolios.state.auth_state import AuthState
from ourportfolios.state.heatmap import HeatmapState
from ourportfolios.state.home_state import HomeState

_DEFAULT_PERIOD = "1D"


class PrefsState(rx.State):
    experience_level: str = "Beginner"
    default_chart_period: str = _DEFAULT_PERIOD
    _pref_explicitly_set: bool = False

    @rx.event
    async def load(self):
        auth = await self.get_state(AuthState)
        if not auth.is_authenticated or not AUTH_AVAILABLE:
            return

        try:
            supabase = get_supabase()
            result = supabase.auth.get_user(auth.auth_token)
            if result is None or result.user is None:
                return
            meta = result.user.user_metadata or {}
            if "default_chart_period" in meta:
                self.default_chart_period = meta["default_chart_period"]
                self._pref_explicitly_set = True
            self.experience_level = meta.get("experience_level", "Beginner")
        except (ValueError, RuntimeError, KeyError):
            pass

    @rx.event
    async def apply_to_heatmap(self):
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
