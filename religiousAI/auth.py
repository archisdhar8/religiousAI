"""
Authentication Module for Divine Wisdom Guide

Handles user registration, login, and session management.
Uses bcrypt for password hashing.
"""

import os
import json
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Tuple
from config import BASE_DIR

# Directory for storing user accounts
USERS_DIR = os.path.join(BASE_DIR, "data", "accounts")
SESSIONS_DIR = os.path.join(BASE_DIR, "data", "sessions")

# Ensure directories exist
os.makedirs(USERS_DIR, exist_ok=True)
os.makedirs(SESSIONS_DIR, exist_ok=True)


def hash_password(password: str) -> str:
    """Hash a password using SHA-256 with salt."""
    salt = secrets.token_hex(16)
    hashed = hashlib.sha256((password + salt).encode()).hexdigest()
    return f"{salt}:{hashed}"


def verify_password(password: str, stored_hash: str) -> bool:
    """Verify a password against its hash."""
    try:
        salt, hashed = stored_hash.split(":")
        check_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        return check_hash == hashed
    except:
        return False


def get_user_file(email: str) -> str:
    """Get the file path for a user account."""
    # Create a safe filename from email
    safe_email = hashlib.md5(email.lower().encode()).hexdigest()
    return os.path.join(USERS_DIR, f"{safe_email}.json")


def user_exists(email: str) -> bool:
    """Check if a user account exists."""
    return os.path.exists(get_user_file(email))


def create_user(email: str, password: str, name: Optional[str] = None) -> Tuple[bool, str]:
    """
    Create a new user account.
    
    Returns:
        Tuple of (success, message)
    """
    email = email.lower().strip()
    
    if user_exists(email):
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


def authenticate_user(email: str, password: str) -> Tuple[bool, str, Optional[Dict]]:
    """
    Authenticate a user.
    
    Returns:
        Tuple of (success, message, user_data)
    """
    email = email.lower().strip()
    
    if not user_exists(email):
        return False, "No account found with this email", None
    
    try:
        filepath = get_user_file(email)
        with open(filepath, 'r', encoding='utf-8') as f:
            user_data = json.load(f)
        
        if verify_password(password, user_data.get("password_hash", "")):
            # Update last login
            user_data["last_login"] = datetime.now().isoformat()
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(user_data, f, indent=2)
            
            # Return user data without password hash
            safe_user = {k: v for k, v in user_data.items() if k != "password_hash"}
            return True, "Login successful", safe_user
        else:
            return False, "Incorrect password", None
            
    except Exception as e:
        return False, f"Error during authentication: {str(e)}", None


def get_existing_valid_session(email: str) -> Optional[str]:
    """
    Find an existing valid session for a user.
    
    Returns:
        Session token if found, None otherwise
    """
    email = email.lower()
    
    if not os.path.exists(SESSIONS_DIR):
        return None
    
    try:
        # Check all session files
        for filename in os.listdir(SESSIONS_DIR):
            if not filename.endswith('.json'):
                continue
            
            session_file = os.path.join(SESSIONS_DIR, filename)
            try:
                with open(session_file, 'r', encoding='utf-8') as f:
                    session_data = json.load(f)
                
                # Check if session belongs to this user and is still valid
                if session_data.get("email", "").lower() == email:
                    expires_at = datetime.fromisoformat(session_data["expires_at"])
                    if datetime.now() <= expires_at:
                        # Valid session found, return the token (filename without .json)
                        return filename[:-5]  # Remove .json extension
                    else:
                        # Expired session, delete it
                        try:
                            os.unlink(session_file)
                        except:
                            pass
            except:
                # Skip invalid session files
                continue
        
        return None
    except:
        return None


def cleanup_user_sessions(email: str, keep_token: Optional[str] = None):
    """
    Clean up all sessions for a user, optionally keeping one.
    
    Args:
        email: User email
        keep_token: Optional token to keep (all others will be deleted)
    """
    email = email.lower()
    
    if not os.path.exists(SESSIONS_DIR):
        return
    
    try:
        for filename in os.listdir(SESSIONS_DIR):
            if not filename.endswith('.json'):
                continue
            
            token = filename[:-5]  # Remove .json extension
            
            # Skip the token we want to keep
            if keep_token and token == keep_token:
                continue
            
            session_file = os.path.join(SESSIONS_DIR, filename)
            try:
                with open(session_file, 'r', encoding='utf-8') as f:
                    session_data = json.load(f)
                
                # Delete if it belongs to this user
                if session_data.get("email", "").lower() == email:
                    try:
                        os.unlink(session_file)
                    except:
                        pass
            except:
                # Skip invalid session files
                continue
    except:
        pass


def create_session(email: str, reuse_existing: bool = True) -> str:
    """
    Create a new session token for a user.
    
    Args:
        email: User email
        reuse_existing: If True, reuse existing valid session if available
    
    Returns:
        Session token
    """
    email = email.lower()
    
    # Try to reuse existing valid session if requested
    if reuse_existing:
        existing_token = get_existing_valid_session(email)
        if existing_token:
            return existing_token
    
    # Create new session
    token = secrets.token_urlsafe(32)
    
    session_data = {
        "email": email,
        "created_at": datetime.now().isoformat(),
        "expires_at": (datetime.now() + timedelta(days=7)).isoformat()
    }
    
    session_file = os.path.join(SESSIONS_DIR, f"{token}.json")
    with open(session_file, 'w', encoding='utf-8') as f:
        json.dump(session_data, f, indent=2)
    
    # Clean up old sessions for this user (keep the new one)
    cleanup_user_sessions(email, keep_token=token)
    
    return token


def validate_session(token: str) -> Tuple[bool, Optional[str]]:
    """
    Validate a session token.
    
    Returns:
        Tuple of (is_valid, email)
    """
    session_file = os.path.join(SESSIONS_DIR, f"{token}.json")
    
    if not os.path.exists(session_file):
        return False, None
    
    try:
        with open(session_file, 'r', encoding='utf-8') as f:
            session_data = json.load(f)
        
        expires_at = datetime.fromisoformat(session_data["expires_at"])
        if datetime.now() > expires_at:
            # Session expired, delete it
            os.unlink(session_file)
            return False, None
        
        return True, session_data["email"]
    except:
        return False, None


def delete_session(token: str) -> bool:
    """Delete a session (logout)."""
    session_file = os.path.join(SESSIONS_DIR, f"{token}.json")
    
    if os.path.exists(session_file):
        try:
            os.unlink(session_file)
            return True
        except:
            pass
    return False


def get_user_by_email(email: str) -> Optional[Dict]:
    """Get user data by email (without password hash)."""
    if not user_exists(email):
        return None
    
    try:
        filepath = get_user_file(email)
        with open(filepath, 'r', encoding='utf-8') as f:
            user_data = json.load(f)
        
        # Return without password hash
        return {k: v for k, v in user_data.items() if k != "password_hash"}
    except:
        return None


def update_user_preferences(email: str, preferences: Dict) -> bool:
    """Update user preferences."""
    if not user_exists(email):
        return False
    
    try:
        filepath = get_user_file(email)
        with open(filepath, 'r', encoding='utf-8') as f:
            user_data = json.load(f)
        
        user_data["preferences"].update(preferences)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(user_data, f, indent=2)
        
        return True
    except:
        return False

