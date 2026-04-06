"""Compatibility wrapper for the shared auth config."""

from ...auth_config import (
    AUTH_AVAILABLE,
    DATABASE_URL,
    SUPABASE_ANON_KEY,
    SUPABASE_SITE_URL,
    SUPABASE_URL,
    get_supabase,
    oauth_redirect_url,
)

__all__ = [
    "AUTH_AVAILABLE",
    "DATABASE_URL",
    "SUPABASE_ANON_KEY",
    "SUPABASE_SITE_URL",
    "SUPABASE_URL",
    "get_supabase",
    "oauth_redirect_url",
]
