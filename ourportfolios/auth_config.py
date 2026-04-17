"""Supabase client configuration and auth helpers."""

import os

import httpx
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
                "Run: pip install -r requirements-auth.txt"
            )
        _client = create_client(
            SUPABASE_URL,
            SUPABASE_ANON_KEY,
            options=ClientOptions(flow_type="pkce"),
        )
    return _client


def oauth_redirect_url() -> str:
    return f"{SUPABASE_SITE_URL}/auth/callback"


async def supabase_update_user(access_token: str, updates: dict) -> dict:
    """Update the authenticated user via the Supabase REST API.

    Uses the caller's access token directly instead of the shared singleton
    client, preventing session cross-contamination under concurrency.
    """
    async with httpx.AsyncClient() as http_client:
        response = await http_client.put(
            f"{SUPABASE_URL}/auth/v1/user",
            json=updates,
            headers={
                "Authorization": f"Bearer {access_token}",
                "apikey": SUPABASE_ANON_KEY,
                "Content-Type": "application/json",
            },
        )
    data = response.json()
    if response.status_code >= 400:
        raise Exception(
            data.get("msg") or data.get("error_description") or "Update failed."
        )
    return data
