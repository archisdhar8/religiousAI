"""
Community Matching System for Divine Wisdom Guide

Uses AI to analyze user conversations and match people with similar
spiritual interests, struggles, and growth areas for faith-based connections.
Uses Supabase for data storage.
"""

import os
import json
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from config import BASE_DIR, USE_SUPABASE
from supabase_client import get_supabase_client
from memory import get_user_id_from_email

# Directory for community data (fallback)
COMMUNITY_DIR = os.path.join(BASE_DIR, "data", "community")
PROFILES_DIR = os.path.join(COMMUNITY_DIR, "profiles")
MATCHES_DIR = os.path.join(COMMUNITY_DIR, "matches")

if not USE_SUPABASE:
    os.makedirs(PROFILES_DIR, exist_ok=True)
    os.makedirs(MATCHES_DIR, exist_ok=True)

# Spiritual trait categories for matching
TRAIT_CATEGORIES = {
    "life_stage": [
        "young_adult", "parent", "career_focused", "retired", 
        "student", "caregiver", "transitioning"
    ],
    "spiritual_journey": [
        "seeker", "devout", "questioning", "returning", 
        "exploring", "deepening", "teaching"
    ],
    "primary_interests": [
        "prayer", "meditation", "scripture_study", "community",
        "service", "contemplation", "interfaith", "mysticism"
    ],
    "seeking_support_for": [
        "grief", "anxiety", "relationships", "purpose",
        "forgiveness", "faith_crisis", "gratitude", "growth",
        "parenting", "career", "health", "addiction"
    ],
    "preferred_traditions": [
        "christianity", "islam", "buddhism", "hinduism",
        "judaism", "taoism", "sikhism", "interfaith", "spiritual_not_religious"
    ],
    "connection_style": [
        "listener", "sharer", "mentor", "peer",
        "study_partner", "prayer_partner", "discussion"
    ]
}


def _get_user_id_from_email(email: str) -> Optional[str]:
    """Get user UUID from email for Supabase."""
    if not USE_SUPABASE:
        return None
    
    try:
        supabase = get_supabase_client(use_service_role=False)
        response = supabase.table("users").select("id").eq("email", email.lower().strip()).execute()
        if response.data and len(response.data) > 0:
            return response.data[0]["id"]
    except:
        pass
    return None


def extract_traits_from_themes(themes: List[str], conversations: List[Dict]) -> Dict[str, List[str]]:
    """
    Extract spiritual traits from user's conversation themes and history.
    """
    traits = {
        "life_stage": [],
        "spiritual_journey": [],
        "primary_interests": [],
        "seeking_support_for": [],
        "preferred_traditions": [],
        "connection_style": []
    }
    
    for theme in themes:
        theme_lower = theme.lower()
        
        # Map to seeking_support_for
        if theme_lower in ["grief", "loss"]:
            traits["seeking_support_for"].append("grief")
        elif theme_lower in ["anxiety", "fear", "worry"]:
            traits["seeking_support_for"].append("anxiety")
        elif theme_lower in ["relationships", "family"]:
            traits["seeking_support_for"].append("relationships")
        elif theme_lower in ["purpose", "meaning"]:
            traits["seeking_support_for"].append("purpose")
        elif theme_lower in ["forgiveness", "anger"]:
            traits["seeking_support_for"].append("forgiveness")
        elif theme_lower in ["faith", "doubt"]:
            traits["seeking_support_for"].append("faith_crisis")
        elif theme_lower in ["gratitude", "thankful"]:
            traits["seeking_support_for"].append("gratitude")
        elif theme_lower in ["work", "career"]:
            traits["seeking_support_for"].append("career")
        elif theme_lower in ["health", "illness"]:
            traits["seeking_support_for"].append("health")
    
    # Analyze conversation count for spiritual journey
    if conversations:
        conv_count = len(conversations)
        if conv_count > 20:
            traits["spiritual_journey"].append("deepening")
        elif conv_count > 10:
            traits["spiritual_journey"].append("devout")
        elif conv_count > 5:
            traits["spiritual_journey"].append("exploring")
        else:
            traits["spiritual_journey"].append("seeker")
    
    # Default connection style
    traits["connection_style"].append("peer")
    
    # Remove duplicates
    for key in traits:
        traits[key] = list(set(traits[key]))
    
    return traits


def create_or_update_profile(
    user_email: str,
    display_name: str,
    bio: Optional[str] = None,
    traits: Optional[Dict[str, List[str]]] = None,
    preferred_traditions: Optional[List[str]] = None,
    opt_in: bool = True
) -> Dict:
    """Create or update a user's community profile."""
    if not USE_SUPABASE:
        return _create_or_update_profile_file_based(user_email, display_name, bio, traits, preferred_traditions, opt_in)
    
    user_email = user_email.lower().strip()
    user_id = _get_user_id_from_email(user_email)
    
    if not user_id:
        raise ValueError(f"User not found for email: {user_email}")
    
    try:
        supabase = get_supabase_client(use_service_role=False)
        
        # Get existing profile if it exists
        existing_response = supabase.table("community_profiles").select("*").eq("user_id", user_id).execute()
        existing = existing_response.data[0] if existing_response.data else None
        
        profile_data = {
            "user_id": user_id,
            "display_name": display_name,
            "bio": bio or (existing.get("bio") if existing else ""),
            "traits": traits or (existing.get("traits", {}) if existing else {}),
            "preferred_traditions": preferred_traditions or (existing.get("preferred_traditions", []) if existing else []),
            "opt_in": opt_in,
            "last_active": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        if existing:
            # Update existing profile
            response = supabase.table("community_profiles").update(profile_data).eq("user_id", user_id).execute()
        else:
            # Create new profile
            profile_data["created_at"] = datetime.now().isoformat()
            response = supabase.table("community_profiles").insert(profile_data).execute()
        
        if response.data and len(response.data) > 0:
            profile = response.data[0]
            # Add email for backward compatibility
            profile["email"] = user_email
            return profile
        
        raise Exception("Failed to create/update profile")
        
    except Exception as e:
        print(f"Error creating/updating profile in Supabase: {e}")
        # Fallback to file-based
        return _create_or_update_profile_file_based(user_email, display_name, bio, traits, preferred_traditions, opt_in)


def get_profile(user_email: str) -> Optional[Dict]:
    """Get a user's community profile."""
    if not USE_SUPABASE:
        return _get_profile_file_based(user_email)
    
    user_email = user_email.lower().strip()
    user_id = _get_user_id_from_email(user_email)
    
    if not user_id:
        return None
    
    try:
        supabase = get_supabase_client(use_service_role=False)
        response = supabase.table("community_profiles").select("*").eq("user_id", user_id).execute()
        
        if response.data and len(response.data) > 0:
            profile = response.data[0]
            # Add email and connections for backward compatibility
            profile["email"] = user_email
            
            # Get connections
            connections_response = supabase.table("connections").select("connected_user_id").eq("user_id", user_id).execute()
            profile["connections"] = [c["connected_user_id"] for c in (connections_response.data or [])]
            
            # Get pending requests
            requests_response = supabase.table("connection_requests").select("*").eq("to_user_id", user_id).eq("status", "pending").execute()
            profile["connection_requests"] = [
                {
                    "from_email": r["from_user_id"],  # This will be user_id, need to get email
                    "from_name": "",  # Will need to join with users table
                    "message": r.get("message", ""),
                    "sent_at": r.get("created_at", "")
                }
                for r in (requests_response.data or [])
            ]
            
            return profile
        
        return None
    except Exception as e:
        print(f"Error getting profile from Supabase: {e}")
        return _get_profile_file_based(user_email)


def calculate_compatibility_score(profile1: Dict, profile2: Dict) -> Tuple[float, List[str]]:
    """Calculate compatibility score between two profiles."""
    if not profile1.get("opt_in") or not profile2.get("opt_in"):
        return 0, []
    
    score = 0
    matching_traits = []
    
    traits1 = profile1.get("traits", {})
    traits2 = profile2.get("traits", {})
    
    weights = {
        "seeking_support_for": 30,
        "preferred_traditions": 25,
        "spiritual_journey": 20,
        "primary_interests": 15,
        "connection_style": 10,
    }
    
    for category, weight in weights.items():
        set1 = set(traits1.get(category, []))
        set2 = set(traits2.get(category, []))
        
        if set1 and set2:
            overlap = set1 & set2
            if overlap:
                overlap_score = len(overlap) / max(len(set1), len(set2))
                score += weight * overlap_score
                matching_traits.extend([f"{category}:{t}" for t in overlap])
    
    trad1 = set(profile1.get("preferred_traditions", []))
    trad2 = set(profile2.get("preferred_traditions", []))
    if trad1 & trad2:
        score += 10
        matching_traits.append(f"traditions:{list(trad1 & trad2)}")
    
    return min(100, score), matching_traits


def find_matches(user_email: str, limit: int = 10) -> List[Dict]:
    """Find compatible matches for a user."""
    user_profile = get_profile(user_email)
    if not user_profile or not user_profile.get("opt_in"):
        return []
    
    if not USE_SUPABASE:
        return _find_matches_file_based(user_email, limit)
    
    user_id = _get_user_id_from_email(user_email)
    if not user_id:
        return []
    
    try:
        supabase = get_supabase_client(use_service_role=False)
        
        # Get all opted-in profiles except self
        profiles_response = supabase.table("community_profiles").select("*").eq("opt_in", True).neq("user_id", user_id).execute()
        
        if not profiles_response.data:
            return []
        
        matches = []
        
        for other_profile in profiles_response.data:
            # Get other user's email
            other_user_response = supabase.table("users").select("email").eq("id", other_profile["user_id"]).execute()
            if not other_user_response.data:
                continue
            
            other_email = other_user_response.data[0]["email"]
            other_profile["email"] = other_email
            
            # Calculate compatibility
            score, matching_traits = calculate_compatibility_score(user_profile, other_profile)
            
            if score >= 20:  # Minimum threshold
                matches.append({
                    "email": other_email,
                    "display_name": other_profile.get("display_name", ""),
                    "bio": other_profile.get("bio", "")[:100],
                    "compatibility_score": round(score),
                    "matching_traits": matching_traits[:5],
                    "preferred_traditions": other_profile.get("preferred_traditions", []),
                    "last_active": other_profile.get("last_active", ""),
                })
        
        # Sort by compatibility score
        matches.sort(key=lambda x: x["compatibility_score"], reverse=True)
        
        return matches[:limit]
        
    except Exception as e:
        print(f"Error finding matches in Supabase: {e}")
        return _find_matches_file_based(user_email, limit)


def send_connection_request(from_email: str, to_email: str, message: str = "") -> Tuple[bool, str]:
    """Send a connection request to another user."""
    if not USE_SUPABASE:
        return _send_connection_request_file_based(from_email, to_email, message)
    
    from_email = from_email.lower().strip()
    to_email = to_email.lower().strip()
    
    from_user_id = _get_user_id_from_email(from_email)
    to_user_id = _get_user_id_from_email(to_email)
    
    if not from_user_id:
        return False, "Your profile not found. Please create a profile first."
    if not to_user_id:
        return False, "User not found."
    
    try:
        supabase = get_supabase_client(use_service_role=False)
        
        # Check if to_user has opted in
        to_profile_response = supabase.table("community_profiles").select("opt_in").eq("user_id", to_user_id).execute()
        if not to_profile_response.data or not to_profile_response.data[0].get("opt_in"):
            return False, "User is not accepting connections."
        
        # Check if already connected
        existing_connection = supabase.table("connections").select("id").eq("user_id", from_user_id).eq("connected_user_id", to_user_id).execute()
        if existing_connection.data:
            return False, "You are already connected with this user."
        
        # Check if request already exists
        existing_request = supabase.table("connection_requests").select("id").eq("from_user_id", from_user_id).eq("to_user_id", to_user_id).eq("status", "pending").execute()
        if existing_request.data:
            return False, "Connection request already sent."
        
        # Get from_user's display name
        from_profile_response = supabase.table("community_profiles").select("display_name").eq("user_id", from_user_id).execute()
        from_name = from_profile_response.data[0].get("display_name", "") if from_profile_response.data else ""
        
        # Create connection request
        request_data = {
            "from_user_id": from_user_id,
            "to_user_id": to_user_id,
            "message": message[:200],
            "status": "pending",
            "created_at": datetime.now().isoformat()
        }
        
        supabase.table("connection_requests").insert(request_data).execute()
        
        return True, "Connection request sent!"
        
    except Exception as e:
        print(f"Error sending connection request in Supabase: {e}")
        return False, f"Error: {str(e)}"


def respond_to_request(user_email: str, from_email: str, accept: bool) -> Tuple[bool, str]:
    """Accept or decline a connection request."""
    if not USE_SUPABASE:
        return _respond_to_request_file_based(user_email, from_email, accept)
    
    user_email = user_email.lower().strip()
    from_email = from_email.lower().strip()
    
    user_id = _get_user_id_from_email(user_email)
    from_user_id = _get_user_id_from_email(from_email)
    
    if not user_id or not from_user_id:
        return False, "Profile not found."
    
    try:
        supabase = get_supabase_client(use_service_role=False)
        
        # Find the request
        request_response = supabase.table("connection_requests").select("*").eq("from_user_id", from_user_id).eq("to_user_id", user_id).eq("status", "pending").execute()
        
        if not request_response.data:
            return False, "Connection request not found."
        
        # Update request status
        new_status = "accepted" if accept else "declined"
        supabase.table("connection_requests").update({
            "status": new_status,
            "responded_at": datetime.now().isoformat()
        }).eq("from_user_id", from_user_id).eq("to_user_id", user_id).execute()
        
        # If accepted, create bidirectional connections (trigger handles this, but we can also do it here)
        if accept:
            # Connection will be created by database trigger, but we can also insert directly
            try:
                supabase.table("connections").insert({
                    "user_id": user_id,
                    "connected_user_id": from_user_id
                }).execute()
                supabase.table("connections").insert({
                    "user_id": from_user_id,
                    "connected_user_id": user_id
                }).execute()
            except:
                # May already exist from trigger
                pass
        
        message = "Connection accepted!" if accept else "Connection declined."
        return True, message
        
    except Exception as e:
        print(f"Error responding to connection request in Supabase: {e}")
        return False, f"Error: {str(e)}"


def get_connections(user_email: str) -> List[Dict]:
    """Get a user's connections with profile info."""
    if not USE_SUPABASE:
        return _get_connections_file_based(user_email)
    
    user_email = user_email.lower().strip()
    user_id = _get_user_id_from_email(user_email)
    
    if not user_id:
        return []
    
    try:
        supabase = get_supabase_client(use_service_role=False)
        
        # Get connections
        connections_response = supabase.table("connections").select("connected_user_id").eq("user_id", user_id).execute()
        
        if not connections_response.data:
            return []
        
        connections = []
        for conn in connections_response.data:
            connected_user_id = conn["connected_user_id"]
            
            # Get connected user's profile
            profile_response = supabase.table("community_profiles").select("*").eq("user_id", connected_user_id).execute()
            if not profile_response.data:
                continue
            
            profile = profile_response.data[0]
            
            # Get email
            user_response = supabase.table("users").select("email").eq("id", connected_user_id).execute()
            email = user_response.data[0].get("email", "") if user_response.data else ""
            
            connections.append({
                "email": email,
                "display_name": profile.get("display_name", ""),
                "bio": profile.get("bio", "")[:100],
                "preferred_traditions": profile.get("preferred_traditions", []),
                "last_active": profile.get("last_active", ""),
            })
        
        return connections
        
    except Exception as e:
        print(f"Error getting connections from Supabase: {e}")
        return _get_connections_file_based(user_email)


def get_pending_requests(user_email: str) -> List[Dict]:
    """Get pending connection requests for a user."""
    if not USE_SUPABASE:
        return _get_pending_requests_file_based(user_email)
    
    user_email = user_email.lower().strip()
    user_id = _get_user_id_from_email(user_email)
    
    if not user_id:
        return []
    
    try:
        supabase = get_supabase_client(use_service_role=False)
        
        # Get pending requests
        requests_response = supabase.table("connection_requests").select("*").eq("to_user_id", user_id).eq("status", "pending").execute()
        
        if not requests_response.data:
            return []
        
        requests = []
        for req in requests_response.data:
            from_user_id = req["from_user_id"]
            
            # Get from_user's email and profile
            user_response = supabase.table("users").select("email").eq("id", from_user_id).execute()
            email = user_response.data[0].get("email", "") if user_response.data else ""
            
            profile_response = supabase.table("community_profiles").select("display_name").eq("user_id", from_user_id).execute()
            display_name = profile_response.data[0].get("display_name", "") if profile_response.data else ""
            
            requests.append({
                "from_email": email,
                "from_name": display_name,
                "message": req.get("message", ""),
                "sent_at": req.get("created_at", "")
            })
        
        return requests
        
    except Exception as e:
        print(f"Error getting pending requests from Supabase: {e}")
        return _get_pending_requests_file_based(user_email)


# =====================================================================
# FILE-BASED FALLBACK FUNCTIONS
# =====================================================================

def _get_profile_path(user_email: str) -> str:
    """Get the file path for a user's community profile."""
    import hashlib
    safe_id = hashlib.md5(user_email.lower().encode()).hexdigest()
    return os.path.join(PROFILES_DIR, f"{safe_id}.json")


def _create_or_update_profile_file_based(
    user_email: str,
    display_name: str,
    bio: Optional[str] = None,
    traits: Optional[Dict[str, List[str]]] = None,
    preferred_traditions: Optional[List[str]] = None,
    opt_in: bool = True
) -> Dict:
    """Fallback file-based profile creation."""
    profile_path = _get_profile_path(user_email)
    
    existing = {}
    if os.path.exists(profile_path):
        with open(profile_path, 'r') as f:
            existing = json.load(f)
    
    profile = {
        "email": user_email.lower(),
        "display_name": display_name,
        "bio": bio or existing.get("bio", ""),
        "traits": traits or existing.get("traits", {}),
        "preferred_traditions": preferred_traditions or existing.get("preferred_traditions", []),
        "opt_in": opt_in,
        "created_at": existing.get("created_at", datetime.now().isoformat()),
        "updated_at": datetime.now().isoformat(),
        "last_active": datetime.now().isoformat(),
        "connections": existing.get("connections", []),
        "connection_requests": existing.get("connection_requests", []),
    }
    
    with open(profile_path, 'w') as f:
        json.dump(profile, f, indent=2)
    
    return profile


def _get_profile_file_based(user_email: str) -> Optional[Dict]:
    """Fallback file-based profile retrieval."""
    profile_path = _get_profile_path(user_email)
    
    if not os.path.exists(profile_path):
        return None
    
    with open(profile_path, 'r') as f:
        return json.load(f)


def _find_matches_file_based(user_email: str, limit: int = 10) -> List[Dict]:
    """Fallback file-based match finding."""
    user_profile = _get_profile_file_based(user_email)
    if not user_profile or not user_profile.get("opt_in"):
        return []
    
    matches = []
    
    for filename in os.listdir(PROFILES_DIR):
        if not filename.endswith(".json"):
            continue
        
        profile_path = os.path.join(PROFILES_DIR, filename)
        with open(profile_path, 'r') as f:
            other_profile = json.load(f)
        
        if other_profile["email"] == user_email.lower():
            continue
        if not other_profile.get("opt_in"):
            continue
        
        score, matching_traits = calculate_compatibility_score(user_profile, other_profile)
        
        if score >= 20:
            matches.append({
                "email": other_profile["email"],
                "display_name": other_profile["display_name"],
                "bio": other_profile.get("bio", "")[:100],
                "compatibility_score": round(score),
                "matching_traits": matching_traits[:5],
                "preferred_traditions": other_profile.get("preferred_traditions", []),
                "last_active": other_profile.get("last_active", ""),
            })
    
    matches.sort(key=lambda x: x["compatibility_score"], reverse=True)
    return matches[:limit]


def _send_connection_request_file_based(from_email: str, to_email: str, message: str = "") -> Tuple[bool, str]:
    """Fallback file-based connection request."""
    from_profile = _get_profile_file_based(from_email)
    to_profile = _get_profile_file_based(to_email)
    
    if not from_profile:
        return False, "Your profile not found. Please create a profile first."
    if not to_profile:
        return False, "User not found."
    if not to_profile.get("opt_in"):
        return False, "User is not accepting connections."
    
    if to_email.lower() in from_profile.get("connections", []):
        return False, "You are already connected with this user."
    
    existing_requests = to_profile.get("connection_requests", [])
    if any(r["from_email"] == from_email.lower() for r in existing_requests):
        return False, "Connection request already sent."
    
    request = {
        "from_email": from_email.lower(),
        "from_name": from_profile["display_name"],
        "message": message[:200],
        "sent_at": datetime.now().isoformat()
    }
    
    to_profile["connection_requests"] = existing_requests + [request]
    
    to_path = _get_profile_path(to_email)
    with open(to_path, 'w') as f:
        json.dump(to_profile, f, indent=2)
    
    return True, "Connection request sent!"


def _respond_to_request_file_based(user_email: str, from_email: str, accept: bool) -> Tuple[bool, str]:
    """Fallback file-based request response."""
    user_profile = _get_profile_file_based(user_email)
    from_profile = _get_profile_file_based(from_email)
    
    if not user_profile or not from_profile:
        return False, "Profile not found."
    
    requests = user_profile.get("connection_requests", [])
    request = None
    for r in requests:
        if r["from_email"] == from_email.lower():
            request = r
            break
    
    if not request:
        return False, "Connection request not found."
    
    user_profile["connection_requests"] = [r for r in requests if r["from_email"] != from_email.lower()]
    
    if accept:
        user_connections = user_profile.get("connections", [])
        from_connections = from_profile.get("connections", [])
        
        if from_email.lower() not in user_connections:
            user_profile["connections"] = user_connections + [from_email.lower()]
        if user_email.lower() not in from_connections:
            from_profile["connections"] = from_connections + [user_email.lower()]
        
        from_path = _get_profile_path(from_email)
        with open(from_path, 'w') as f:
            json.dump(from_profile, f, indent=2)
        
        message = "Connection accepted!"
    else:
        message = "Connection declined."
    
    user_path = _get_profile_path(user_email)
    with open(user_path, 'w') as f:
        json.dump(user_profile, f, indent=2)
    
    return True, message


def _get_connections_file_based(user_email: str) -> List[Dict]:
    """Fallback file-based connections retrieval."""
    profile = _get_profile_file_based(user_email)
    if not profile:
        return []
    
    connections = []
    for email in profile.get("connections", []):
        conn_profile = _get_profile_file_based(email)
        if conn_profile:
            connections.append({
                "email": conn_profile["email"],
                "display_name": conn_profile["display_name"],
                "bio": conn_profile.get("bio", "")[:100],
                "preferred_traditions": conn_profile.get("preferred_traditions", []),
                "last_active": conn_profile.get("last_active", ""),
            })
    
    return connections


def _get_pending_requests_file_based(user_email: str) -> List[Dict]:
    """Fallback file-based pending requests retrieval."""
    profile = _get_profile_file_based(user_email)
    if not profile:
        return []
    
    return profile.get("connection_requests", [])
