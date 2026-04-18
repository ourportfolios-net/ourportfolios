"""Place at: ourportfolios/state/supabase_client.py
Moved here from pages/auth/client.py to avoid circular imports.
auth_state.py imports from this file; pages import from auth_state — no cycle.
"""

import os

from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL: str = os.environ.get("SUPABASE_URL", "")
SUPABASE_ANON_KEY: str = os.environ.get("SUPABASE_ANON_KEY", "")
SUPABASE_SITE_URL: str = os.environ.get("SITE_URL") or "http://localhost:3000"
DATABASE_URL: str = os.environ.get("DATABASE_URL", "")

AUTH_AVAILABLE: bool = bool(SUPABASE_URL and SUPABASE_ANON_KEY)

_client = None


def get_supabase():
    global _client
    if _client is None:
        try:
            from supabase import ClientOptions, create_client
        except ImportError:
            raise RuntimeError(
                "SUPABASE_URL and SUPABASE_ANON_KEY are set but 'supabase' is not installed.\n"
                "Run: pip install -r requirements-auth.txt",
            )
        _client = create_client(
            SUPABASE_URL,
            SUPABASE_ANON_KEY,
            options=ClientOptions(flow_type="pkce"),
        )
    return _client


def oauth_redirect_url() -> str:
    return f"{SUPABASE_SITE_URL}/auth/callback"
