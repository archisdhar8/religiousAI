"""
Supabase Client Configuration for Divine Wisdom Guide

Initializes and provides Supabase client instances for database operations.
"""

import os
from supabase import create_client, Client
from typing import Optional

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Supabase configuration from environment variables
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")


def get_supabase_client(use_service_role: bool = False) -> Optional[Client]:
    """
    Get a Supabase client instance.
    
    Args:
        use_service_role: If True, use service role key (bypasses RLS).
                         If False, use anon key (respects RLS).
                         Default: False
    
    Returns:
        Supabase Client instance, or None if configuration is missing
    """
    if not SUPABASE_URL:
        raise ValueError("SUPABASE_URL environment variable is not set")
    
    key = SUPABASE_SERVICE_ROLE_KEY if use_service_role else SUPABASE_ANON_KEY
    
    if not key:
        raise ValueError(
            f"SUPABASE_{'SERVICE_ROLE' if use_service_role else 'ANON'}_KEY "
            "environment variable is not set"
        )
    
    return create_client(SUPABASE_URL, key)


# Default client instance (uses anon key, respects RLS)
# Use this for normal operations where RLS should be enforced
supabase: Optional[Client] = None

# Service role client (bypasses RLS)
# Use this only for admin operations or migrations
supabase_admin: Optional[Client] = None


def initialize_clients():
    """Initialize Supabase client instances."""
    global supabase, supabase_admin
    
    try:
        supabase = get_supabase_client(use_service_role=False)
        supabase_admin = get_supabase_client(use_service_role=True)
        print("✓ Supabase clients initialized successfully")
    except Exception as e:
        print(f"✗ Error initializing Supabase clients: {e}")
        raise


# Auto-initialize on import (optional - can be called manually instead)
# Uncomment the line below if you want clients to initialize automatically
# initialize_clients()

