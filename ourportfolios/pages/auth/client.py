"""
Place at: ourportfolios/pages/auth/client.py
"""

import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL: str = os.environ.get("SUPABASE_URL", "")
SUPABASE_ANON_KEY: str = os.environ.get("SUPABASE_ANON_KEY", "")
SUPABASE_SITE_URL: str = os.environ.get("SITE_URL", "http://localhost:3000")
DATABASE_URL: str = os.environ.get("DATABASE_URL", "")

AUTH_AVAILABLE: bool = bool(SUPABASE_URL and SUPABASE_ANON_KEY)

_client = None


def get_supabase():
    global _client
    if _client is None:
        try:
            from supabase import create_client, ClientOptions
        except ImportError:
            raise RuntimeError(
                "SUPABASE_URL and SUPABASE_ANON_KEY are set but 'supabase' is not installed.\n"
            )
        _client = create_client(
            SUPABASE_URL,
            SUPABASE_ANON_KEY,
            options=ClientOptions(flow_type="pkce"),
        )
    return _client


def oauth_redirect_url() -> str:
    return f"{SUPABASE_SITE_URL}/auth/callback"
