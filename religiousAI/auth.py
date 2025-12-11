"""
Authentication Module for Divine Wisdom Guide

Handles user registration, login, and session management using Supabase Auth.
"""

import os
from datetime import datetime
from typing import Optional, Dict, Tuple
from supabase_client import get_supabase_client
from config import USE_SUPABASE

# Fallback to file-based auth if Supabase is disabled
if not USE_SUPABASE:
    import json
    import hashlib
    import secrets
    from datetime import timedelta
    from config import BASE_DIR
    
    USERS_DIR = os.path.join(BASE_DIR, "data", "accounts")
    SESSIONS_DIR = os.path.join(BASE_DIR, "data", "sessions")
    os.makedirs(USERS_DIR, exist_ok=True)
    os.makedirs(SESSIONS_DIR, exist_ok=True)


def create_user(email: str, password: str, name: Optional[str] = None) -> Tuple[bool, str]:
    """
    Create a new user account using Supabase Auth.
    
    Returns:
        Tuple of (success, message)
    """
    if not USE_SUPABASE:
        # Fallback to file-based auth
        return _create_user_file_based(email, password, name)
    
    email = email.lower().strip()
    
    if len(password) < 6:
        return False, "Password must be at least 6 characters"
    
    try:
        supabase = get_supabase_client(use_service_role=False)
        
        # Sign up user with Supabase Auth
        auth_response = supabase.auth.sign_up({
            "email": email,
            "password": password,
            "options": {
                "data": {
                    "name": name or email.split("@")[0]
                }
            }
        })
        
        if auth_response.user is None:
            return False, "Failed to create account"
        
        user_id = auth_response.user.id
        
        # Create user profile in public.users table
        try:
            supabase.table("users").insert({
                "id": user_id,
                "email": email,
                "name": name or email.split("@")[0],
                "preferences": {
                    "default_religion": "christianity",
                    "theme": "dark"
                },
                "created_at": datetime.now().isoformat(),
                "visit_count": 0
            }).execute()
        except Exception as e:
            # User might already exist in auth, but not in public.users
            # Try to update instead
            try:
                supabase.table("users").update({
                    "name": name or email.split("@")[0],
                    "preferences": {
                        "default_religion": "christianity",
                        "theme": "dark"
                    }
                }).eq("id", user_id).execute()
            except:
                pass
        
        return True, "Account created successfully"
        
    except Exception as e:
        error_msg = str(e)
        if "already registered" in error_msg.lower() or "already exists" in error_msg.lower():
            return False, "An account with this email already exists"
        return False, f"Error creating account: {error_msg}"


def authenticate_user(email: str, password: str) -> Tuple[bool, str, Optional[Dict]]:
    """
    Authenticate a user using Supabase Auth.
    
    Returns:
        Tuple of (success, message, user_data)
    """
    if not USE_SUPABASE:
        return _authenticate_user_file_based(email, password)
    
    email = email.lower().strip()
    
    try:
        supabase = get_supabase_client(use_service_role=False)
        
        # Sign in with Supabase Auth
        auth_response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        
        if auth_response.user is None:
            return False, "Invalid email or password", None
        
        user_id = auth_response.user.id
        
        # Get user profile from public.users table
        user_response = supabase.table("users").select("*").eq("id", user_id).execute()
        
        if user_response.data:
            user_data = user_response.data[0]
        else:
            # Create user profile if it doesn't exist
            user_data = {
                "id": user_id,
                "email": email,
                "name": email.split("@")[0],
                "preferences": {
                    "default_religion": "christianity",
                    "theme": "dark"
                },
                "created_at": datetime.now().isoformat(),
                "visit_count": 0
            }
            supabase.table("users").insert(user_data).execute()
        
        # Update last_login
        supabase.table("users").update({
            "last_login": datetime.now().isoformat()
        }).eq("id", user_id).execute()
        
        # Return user data without sensitive fields
        safe_user = {
            "email": user_data.get("email"),
            "name": user_data.get("name"),
            "created_at": user_data.get("created_at"),
            "preferences": user_data.get("preferences", {})
        }
        
        return True, "Login successful", safe_user
        
    except Exception as e:
        error_msg = str(e)
        if "invalid" in error_msg.lower() or "wrong" in error_msg.lower():
            return False, "Invalid email or password", None
        return False, f"Error during authentication: {error_msg}", None


def create_session(email: str, reuse_existing: bool = True) -> str:
    """
    Create a session token for a user.
    With Supabase, this returns the access token from the auth session.
    
    Note: With Supabase Auth, sessions are managed automatically.
    This function is kept for backward compatibility but returns the access token.
    """
    if not USE_SUPABASE:
        return _create_session_file_based(email, reuse_existing)
    
    # With Supabase, sessions are created during sign_in_with_password
    # This function is mainly for backward compatibility
    # The actual session token should come from the auth response
    # For now, we'll need to get it from the current session
    try:
        supabase = get_supabase_client(use_service_role=False)
        session = supabase.auth.get_session()
        if session and session.access_token:
            return session.access_token
    except:
        pass
    
    # If no session exists, return empty string (caller should handle this)
    return ""


def validate_session(token: str) -> Tuple[bool, Optional[str]]:
    """
    Validate a session token using Supabase Auth.
    
    Args:
        token: Access token (Bearer token) from Supabase Auth
    
    Returns:
        Tuple of (is_valid, email)
    """
    if not USE_SUPABASE:
        return _validate_session_file_based(token)
    
    try:
        # Remove "Bearer " prefix if present
        if token.startswith("Bearer "):
            token = token[7:]
        
        supabase = get_supabase_client(use_service_role=False)
        
        # Get the user from the token
        user_response = supabase.auth.get_user(token)
        
        if user_response and user_response.user:
            # Get email from auth.users or from public.users
            email = user_response.user.email
            if email:
                return True, email
            
            # Fallback: get email from public.users table
            user_id = user_response.user.id
            user_data = supabase.table("users").select("email").eq("id", user_id).execute()
            if user_data.data and len(user_data.data) > 0:
                return True, user_data.data[0].get("email")
        
        return False, None
            
    except Exception as e:
        return False, None


def delete_session(token: str) -> bool:
    """Delete a session (logout) using Supabase Auth."""
    if not USE_SUPABASE:
        return _delete_session_file_based(token)
    
    try:
        supabase = get_supabase_client(use_service_role=False)
        supabase.auth.sign_out()
        return True
    except:
        return False


def get_user_by_email(email: str) -> Optional[Dict]:
    """Get user data by email from Supabase."""
    if not USE_SUPABASE:
        return _get_user_by_email_file_based(email)
    
    email = email.lower().strip()
    
    try:
        supabase = get_supabase_client(use_service_role=False)
        response = supabase.table("users").select("*").eq("email", email).execute()
        
        if response.data and len(response.data) > 0:
            user_data = response.data[0]
            # Return without sensitive fields
            return {
                "email": user_data.get("email"),
                "name": user_data.get("name"),
                "created_at": user_data.get("created_at"),
                "preferences": user_data.get("preferences", {})
            }
        return None
    except:
        return None


def update_user_preferences(email: str, preferences: Dict) -> bool:
    """Update user preferences in Supabase."""
    if not USE_SUPABASE:
        return _update_user_preferences_file_based(email, preferences)
    
    email = email.lower().strip()
    
    try:
        supabase = get_supabase_client(use_service_role=False)
        response = supabase.table("users").update({
            "preferences": preferences
        }).eq("email", email).execute()
        
        return response.data is not None and len(response.data) > 0
    except:
        return False


# =====================================================================
# FILE-BASED AUTH FALLBACK (for backward compatibility)
# =====================================================================

def _create_user_file_based(email: str, password: str, name: Optional[str] = None) -> Tuple[bool, str]:
    """Fallback file-based user creation."""
    import json
    import hashlib
    import secrets
    
    def hash_password(password: str) -> str:
        salt = secrets.token_hex(16)
        hashed = hashlib.sha256((password + salt).encode()).hexdigest()
        return f"{salt}:{hashed}"
    
    def get_user_file(email: str) -> str:
        safe_email = hashlib.md5(email.lower().encode()).hexdigest()
        return os.path.join(USERS_DIR, f"{safe_email}.json")
    
    email = email.lower().strip()
    
    if os.path.exists(get_user_file(email)):
        return False, "An account with this email already exists"
    
    if len(password) < 6:
        return False, "Password must be at least 6 characters"
    
    user_data = {
        "email": email,
        "password_hash": hash_password(password),
        "name": name or email.split("@")[0],
        "created_at": datetime.now().isoformat(),
        "last_login": None,
        "preferences": {
            "default_religion": "christianity",
            "theme": "dark"
        }
    }
    
    try:
        filepath = get_user_file(email)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(user_data, f, indent=2)
        return True, "Account created successfully"
    except Exception as e:
        return False, f"Error creating account: {str(e)}"


def _authenticate_user_file_based(email: str, password: str) -> Tuple[bool, str, Optional[Dict]]:
    """Fallback file-based authentication."""
    import json
    import hashlib
    
    def verify_password(password: str, stored_hash: str) -> bool:
        try:
            salt, hashed = stored_hash.split(":")
            check_hash = hashlib.sha256((password + salt).encode()).hexdigest()
            return check_hash == hashed
        except:
            return False
    
    def get_user_file(email: str) -> str:
        safe_email = hashlib.md5(email.lower().encode()).hexdigest()
        return os.path.join(USERS_DIR, f"{safe_email}.json")
    
    email = email.lower().strip()
    filepath = get_user_file(email)
    
    if not os.path.exists(filepath):
        return False, "No account found with this email", None
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            user_data = json.load(f)
        
        if verify_password(password, user_data.get("password_hash", "")):
            user_data["last_login"] = datetime.now().isoformat()
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(user_data, f, indent=2)
            
            safe_user = {k: v for k, v in user_data.items() if k != "password_hash"}
            return True, "Login successful", safe_user
        else:
            return False, "Incorrect password", None
    except Exception as e:
        return False, f"Error during authentication: {str(e)}", None


def _create_session_file_based(email: str, reuse_existing: bool = True) -> str:
    """Fallback file-based session creation."""
    import secrets
    from datetime import timedelta
    
    email = email.lower()
    token = secrets.token_urlsafe(32)
    
    session_data = {
        "email": email,
        "created_at": datetime.now().isoformat(),
        "expires_at": (datetime.now() + timedelta(days=7)).isoformat()
    }
    
    session_file = os.path.join(SESSIONS_DIR, f"{token}.json")
    with open(session_file, 'w', encoding='utf-8') as f:
        json.dump(session_data, f, indent=2)
    
    return token


def _validate_session_file_based(token: str) -> Tuple[bool, Optional[str]]:
    """Fallback file-based session validation."""
    import json
    from datetime import datetime
    
    session_file = os.path.join(SESSIONS_DIR, f"{token}.json")
    
    if not os.path.exists(session_file):
        return False, None
    
    try:
        with open(session_file, 'r', encoding='utf-8') as f:
            session_data = json.load(f)
        
        expires_at = datetime.fromisoformat(session_data["expires_at"])
        if datetime.now() > expires_at:
            os.unlink(session_file)
            return False, None
        
        return True, session_data["email"]
    except:
        return False, None


def _delete_session_file_based(token: str) -> bool:
    """Fallback file-based session deletion."""
    session_file = os.path.join(SESSIONS_DIR, f"{token}.json")
    
    if os.path.exists(session_file):
        try:
            os.unlink(session_file)
            return True
        except:
            pass
    return False


def _get_user_by_email_file_based(email: str) -> Optional[Dict]:
    """Fallback file-based user retrieval."""
    import json
    import hashlib
    
    def get_user_file(email: str) -> str:
        safe_email = hashlib.md5(email.lower().encode()).hexdigest()
        return os.path.join(USERS_DIR, f"{safe_email}.json")
    
    filepath = get_user_file(email)
    
    if not os.path.exists(filepath):
        return None
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            user_data = json.load(f)
        return {k: v for k, v in user_data.items() if k != "password_hash"}
    except:
        return None


def _update_user_preferences_file_based(email: str, preferences: Dict) -> bool:
    """Fallback file-based preferences update."""
    import json
    import hashlib
    
    def get_user_file(email: str) -> str:
        safe_email = hashlib.md5(email.lower().encode()).hexdigest()
        return os.path.join(USERS_DIR, f"{safe_email}.json")
    
    filepath = get_user_file(email)
    
    if not os.path.exists(filepath):
        return False
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            user_data = json.load(f)
        
        user_data["preferences"].update(preferences)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(user_data, f, indent=2)
        
        return True
    except:
        return False
