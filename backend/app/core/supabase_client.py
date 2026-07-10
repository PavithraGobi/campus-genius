"""Supabase client factory.

Uses the service-role key since this is server-side backend code writing
to protected tables (documents, chunks) — never expose this key to the
frontend.
"""

from functools import lru_cache

from supabase import Client, create_client

from app.core.config import settings


@lru_cache
def get_supabase_client() -> Client:
    if not settings.supabase_url or not settings.supabase_service_role_key:
        raise RuntimeError(
            "Supabase is not configured. Set SUPABASE_URL and "
            "SUPABASE_SERVICE_ROLE_KEY in your .env file."
        )
    return create_client(settings.supabase_url, settings.supabase_service_role_key)
