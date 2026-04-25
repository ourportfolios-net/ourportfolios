"""Place at: ourportfolios/state/supabase_client.py.

Moved here from pages/auth/client.py to avoid circular imports.
auth_state.py imports from this file; pages import from auth_state — no cycle.
"""

import functools
import os

from dotenv import load_dotenv
from supabase import Client, ClientOptions, create_client

load_dotenv()

SUPABASE_URL: str = os.environ.get("SUPABASE_URL", "")
SUPABASE_ANON_KEY: str = os.environ.get("SUPABASE_ANON_KEY", "")
SUPABASE_SITE_URL: str = os.environ.get("SITE_URL") or "http://localhost:3000"
DATABASE_URL: str = os.environ.get("DATABASE_URL", "")

AUTH_AVAILABLE: bool = bool(SUPABASE_URL and SUPABASE_ANON_KEY)


@functools.lru_cache(maxsize=1)
def get_supabase() -> Client:
    """Return a memoized Supabase client instance."""
    return create_client(
        SUPABASE_URL,
        SUPABASE_ANON_KEY,
        options=ClientOptions(flow_type="pkce"),
    )


def oauth_redirect_url() -> str:
    """Return the absolute URL for the OAuth callback."""
    return f"{SUPABASE_SITE_URL}/auth/callback"
