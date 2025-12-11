"""
Full-Text Search Module for Divine Wisdom Guide

Provides search functionality for chats and journal entries using Supabase.
"""

from typing import List, Dict, Optional
from supabase_client import get_supabase_client
from config import USE_SUPABASE


def search_chat_messages(user_id: str, query: str, limit: int = 20) -> List[Dict]:
    """
    Search chat messages for a user using full-text search.
    
    Args:
        user_id: User's UUID
        query: Search query string
        limit: Maximum number of results
    
    Returns:
        List of matching messages with chat context
    """
    if not USE_SUPABASE:
        return []
    
    try:
        supabase = get_supabase_client(use_service_role=False)
        
        # Get user's chat IDs
        chats_response = supabase.table("chats").select("id").eq("user_id", user_id).execute()
        chat_ids = [c["id"] for c in (chats_response.data or [])]
        
        if not chat_ids:
            return []
        
        # Search messages using PostgreSQL full-text search
        # Note: This uses the tsvector index created in the schema
        # The search is done via raw SQL since Supabase client doesn't have direct FTS support
        # For now, we'll do a simple text search
        
        messages_response = supabase.table("chat_messages").select(
            "id, chat_id, role, content, timestamp, chats!inner(title)"
        ).in_("chat_id", chat_ids).ilike("content", f"%{query}%").limit(limit).execute()
        
        if not messages_response.data:
            return []
        
        results = []
        for msg in messages_response.data:
            results.append({
                "id": msg["id"],
                "chat_id": msg["chat_id"],
                "chat_title": msg.get("chats", {}).get("title", "Untitled") if isinstance(msg.get("chats"), dict) else "Untitled",
                "role": msg["role"],
                "content": msg["content"],
                "timestamp": msg["timestamp"],
                "snippet": _get_snippet(msg["content"], query)
            })
        
        return results
        
    except Exception as e:
        print(f"Error searching chat messages: {e}")
        return []


def search_journal_entries(user_id: str, query: str, limit: int = 20) -> List[Dict]:
    """
    Search journal entries for a user using full-text search.
    
    Args:
        user_id: User's UUID
        query: Search query string
        limit: Maximum number of results
    
    Returns:
        List of matching journal entries
    """
    if not USE_SUPABASE:
        return []
    
    try:
        supabase = get_supabase_client(use_service_role=False)
        
        # Search journal entries
        entries_response = supabase.table("journal_entries").select(
            "id, entry, reflection, created_at"
        ).eq("user_id", user_id).or_(f"entry.ilike.%{query}%,reflection.ilike.%{query}%").limit(limit).execute()
        
        if not entries_response.data:
            return []
        
        results = []
        for entry in entries_response.data:
            results.append({
                "id": entry["id"],
                "entry": entry["entry"],
                "reflection": entry.get("reflection", ""),
                "created_at": entry["created_at"],
                "snippet": _get_snippet(entry["entry"] + " " + entry.get("reflection", ""), query)
            })
        
        return results
        
    except Exception as e:
        print(f"Error searching journal entries: {e}")
        return []


def search_community_profiles(query: str, limit: int = 20) -> List[Dict]:
    """
    Search community profiles by traits, bio, or display name.
    
    Args:
        query: Search query string
        limit: Maximum number of results
    
    Returns:
        List of matching profiles
    """
    if not USE_SUPABASE:
        return []
    
    try:
        supabase = get_supabase_client(use_service_role=False)
        
        # Search profiles
        profiles_response = supabase.table("community_profiles").select(
            "id, user_id, display_name, bio, preferred_traditions, users!inner(email)"
        ).eq("opt_in", True).or_(
            f"display_name.ilike.%{query}%,bio.ilike.%{query}%"
        ).limit(limit).execute()
        
        if not profiles_response.data:
            return []
        
        results = []
        for profile in profiles_response.data:
            user_data = profile.get("users", {})
            if isinstance(user_data, dict):
                email = user_data.get("email", "")
            else:
                email = ""
            
            results.append({
                "id": profile["id"],
                "user_id": profile["user_id"],
                "email": email,
                "display_name": profile.get("display_name", ""),
                "bio": profile.get("bio", "")[:200],
                "preferred_traditions": profile.get("preferred_traditions", []),
                "snippet": _get_snippet(profile.get("bio", ""), query)
            })
        
        return results
        
    except Exception as e:
        print(f"Error searching community profiles: {e}")
        return []


def _get_snippet(text: str, query: str, context_length: int = 100) -> str:
    """Extract a snippet of text around the query match."""
    query_lower = query.lower()
    text_lower = text.lower()
    
    index = text_lower.find(query_lower)
    if index == -1:
        return text[:context_length] + "..." if len(text) > context_length else text
    
    start = max(0, index - context_length // 2)
    end = min(len(text), index + len(query) + context_length // 2)
    
    snippet = text[start:end]
    if start > 0:
        snippet = "..." + snippet
    if end < len(text):
        snippet = snippet + "..."
    
    return snippet

