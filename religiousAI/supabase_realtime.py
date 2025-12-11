"""
Real-time Subscriptions for Divine Wisdom Guide

Provides real-time updates for community features using Supabase Realtime.
"""

from typing import Callable, Optional
from supabase_client import get_supabase_client
from config import USE_SUPABASE


def subscribe_to_connection_requests(
    user_id: str,
    callback: Callable[[dict], None]
) -> Optional[object]:
    """
    Subscribe to real-time connection request updates for a user.
    
    Args:
        user_id: User's UUID
        callback: Function to call when a new request is received
                  Receives dict with request data
    
    Returns:
        Subscription object (can be used to unsubscribe)
    """
    if not USE_SUPABASE:
        return None
    
    try:
        supabase = get_supabase_client(use_service_role=False)
        
        # Subscribe to connection_requests table
        subscription = supabase.table("connection_requests").on(
            "INSERT",
            callback
        ).eq("to_user_id", user_id).eq("status", "pending").subscribe()
        
        return subscription
        
    except Exception as e:
        print(f"Error subscribing to connection requests: {e}")
        return None


def subscribe_to_connection_updates(
    user_id: str,
    callback: Callable[[dict], None]
) -> Optional[object]:
    """
    Subscribe to real-time connection status updates.
    
    Args:
        user_id: User's UUID
        callback: Function to call when connection status changes
                  Receives dict with connection data
    
    Returns:
        Subscription object
    """
    if not USE_SUPABASE:
        return None
    
    try:
        supabase = get_supabase_client(use_service_role=False)
        
        # Subscribe to connection_requests updates (when status changes)
        subscription = supabase.table("connection_requests").on(
            "UPDATE",
            callback
        ).or_(f"from_user_id.eq.{user_id},to_user_id.eq.{user_id}").subscribe()
        
        return subscription
        
    except Exception as e:
        print(f"Error subscribing to connection updates: {e}")
        return None


def subscribe_to_community_activity(
    callback: Callable[[dict], None]
) -> Optional[object]:
    """
    Subscribe to general community activity (new profiles, etc.).
    
    Args:
        callback: Function to call when activity occurs
                  Receives dict with activity data
    
    Returns:
        Subscription object
    """
    if not USE_SUPABASE:
        return None
    
    try:
        supabase = get_supabase_client(use_service_role=False)
        
        # Subscribe to new community profiles
        subscription = supabase.table("community_profiles").on(
            "INSERT",
            callback
        ).eq("opt_in", True).subscribe()
        
        return subscription
        
    except Exception as e:
        print(f"Error subscribing to community activity: {e}")
        return None


def unsubscribe(subscription: object) -> bool:
    """
    Unsubscribe from a real-time subscription.
    
    Args:
        subscription: Subscription object returned from subscribe functions
    
    Returns:
        True if successful, False otherwise
    """
    if not subscription:
        return False
    
    try:
        # Supabase realtime subscriptions have an unsubscribe method
        if hasattr(subscription, 'unsubscribe'):
            subscription.unsubscribe()
            return True
        elif hasattr(subscription, 'close'):
            subscription.close()
            return True
        return False
    except Exception as e:
        print(f"Error unsubscribing: {e}")
        return False

