"""
Community Matching System for Divine Wisdom Guide

Uses AI to analyze user conversations and match people with similar
spiritual interests, struggles, and growth areas for faith-based connections.
"""

import os
import json
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from config import BASE_DIR

# Directory for community data
COMMUNITY_DIR = os.path.join(BASE_DIR, "data", "community")
PROFILES_DIR = os.path.join(COMMUNITY_DIR, "profiles")
MATCHES_DIR = os.path.join(COMMUNITY_DIR, "matches")

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


def get_profile_path(user_email: str) -> str:
    """Get the file path for a user's community profile."""
    import hashlib
    safe_id = hashlib.md5(user_email.lower().encode()).hexdigest()
    return os.path.join(PROFILES_DIR, f"{safe_id}.json")


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
    
    # Map themes to trait categories
    theme_mappings = {
        # seeking_support_for mappings
        "grief": "seeking_support_for",
        "family": "seeking_support_for", 
        "relationships": "seeking_support_for",
        "anxiety": "seeking_support_for",
        "purpose": "seeking_support_for",
        "forgiveness": "seeking_support_for",
        "faith": "seeking_support_for",
        "gratitude": "seeking_support_for",
        "work": "seeking_support_for",
        "health": "seeking_support_for",
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
    
    # Default connection style based on engagement
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
    """
    Create or update a user's community profile.
    """
    profile_path = get_profile_path(user_email)
    
    # Load existing profile if exists
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


def get_profile(user_email: str) -> Optional[Dict]:
    """Get a user's community profile."""
    profile_path = get_profile_path(user_email)
    
    if not os.path.exists(profile_path):
        return None
    
    with open(profile_path, 'r') as f:
        return json.load(f)


def calculate_compatibility_score(profile1: Dict, profile2: Dict) -> Tuple[float, List[str]]:
    """
    Calculate compatibility score between two profiles.
    Returns (score 0-100, list of matching traits).
    """
    if not profile1.get("opt_in") or not profile2.get("opt_in"):
        return 0, []
    
    score = 0
    matching_traits = []
    
    traits1 = profile1.get("traits", {})
    traits2 = profile2.get("traits", {})
    
    # Check trait overlaps with weights
    weights = {
        "seeking_support_for": 30,  # Most important - similar struggles
        "preferred_traditions": 25,  # Shared faith background
        "spiritual_journey": 20,     # Similar stage
        "primary_interests": 15,     # Shared interests
        "connection_style": 10,      # Compatible styles
    }
    
    for category, weight in weights.items():
        set1 = set(traits1.get(category, []))
        set2 = set(traits2.get(category, []))
        
        if set1 and set2:
            overlap = set1 & set2
            if overlap:
                # Score based on overlap percentage
                overlap_score = len(overlap) / max(len(set1), len(set2))
                score += weight * overlap_score
                matching_traits.extend([f"{category}:{t}" for t in overlap])
    
    # Check preferred traditions overlap
    trad1 = set(profile1.get("preferred_traditions", []))
    trad2 = set(profile2.get("preferred_traditions", []))
    if trad1 & trad2:
        score += 10
        matching_traits.append(f"traditions:{list(trad1 & trad2)}")
    
    return min(100, score), matching_traits


def find_matches(user_email: str, limit: int = 10) -> List[Dict]:
    """
    Find compatible matches for a user.
    Returns list of matches with compatibility scores.
    """
    user_profile = get_profile(user_email)
    if not user_profile or not user_profile.get("opt_in"):
        return []
    
    matches = []
    
    # Iterate through all profiles
    for filename in os.listdir(PROFILES_DIR):
        if not filename.endswith(".json"):
            continue
        
        profile_path = os.path.join(PROFILES_DIR, filename)
        with open(profile_path, 'r') as f:
            other_profile = json.load(f)
        
        # Skip self and opted-out users
        if other_profile["email"] == user_email.lower():
            continue
        if not other_profile.get("opt_in"):
            continue
        
        # Calculate compatibility
        score, matching_traits = calculate_compatibility_score(user_profile, other_profile)
        
        if score >= 20:  # Minimum threshold
            matches.append({
                "email": other_profile["email"],
                "display_name": other_profile["display_name"],
                "bio": other_profile.get("bio", "")[:100],
                "compatibility_score": round(score),
                "matching_traits": matching_traits[:5],  # Top 5 matches
                "preferred_traditions": other_profile.get("preferred_traditions", []),
                "last_active": other_profile.get("last_active", ""),
            })
    
    # Sort by compatibility score
    matches.sort(key=lambda x: x["compatibility_score"], reverse=True)
    
    return matches[:limit]


def send_connection_request(from_email: str, to_email: str, message: str = "") -> Tuple[bool, str]:
    """
    Send a connection request to another user.
    """
    from_profile = get_profile(from_email)
    to_profile = get_profile(to_email)
    
    if not from_profile:
        return False, "Your profile not found. Please create a profile first."
    if not to_profile:
        return False, "User not found."
    if not to_profile.get("opt_in"):
        return False, "User is not accepting connections."
    
    # Check if already connected
    if to_email.lower() in from_profile.get("connections", []):
        return False, "You are already connected with this user."
    
    # Check if request already sent
    existing_requests = to_profile.get("connection_requests", [])
    if any(r["from_email"] == from_email.lower() for r in existing_requests):
        return False, "Connection request already sent."
    
    # Add request
    request = {
        "from_email": from_email.lower(),
        "from_name": from_profile["display_name"],
        "message": message[:200],
        "sent_at": datetime.now().isoformat()
    }
    
    to_profile["connection_requests"] = existing_requests + [request]
    
    to_path = get_profile_path(to_email)
    with open(to_path, 'w') as f:
        json.dump(to_profile, f, indent=2)
    
    return True, "Connection request sent!"


def respond_to_request(user_email: str, from_email: str, accept: bool) -> Tuple[bool, str]:
    """
    Accept or decline a connection request.
    """
    user_profile = get_profile(user_email)
    from_profile = get_profile(from_email)
    
    if not user_profile or not from_profile:
        return False, "Profile not found."
    
    # Find and remove the request
    requests = user_profile.get("connection_requests", [])
    request = None
    for r in requests:
        if r["from_email"] == from_email.lower():
            request = r
            break
    
    if not request:
        return False, "Connection request not found."
    
    # Remove request
    user_profile["connection_requests"] = [r for r in requests if r["from_email"] != from_email.lower()]
    
    if accept:
        # Add to both users' connections
        user_connections = user_profile.get("connections", [])
        from_connections = from_profile.get("connections", [])
        
        if from_email.lower() not in user_connections:
            user_profile["connections"] = user_connections + [from_email.lower()]
        if user_email.lower() not in from_connections:
            from_profile["connections"] = from_connections + [user_email.lower()]
        
        # Save from_profile
        from_path = get_profile_path(from_email)
        with open(from_path, 'w') as f:
            json.dump(from_profile, f, indent=2)
        
        message = "Connection accepted!"
    else:
        message = "Connection declined."
    
    # Save user_profile
    user_path = get_profile_path(user_email)
    with open(user_path, 'w') as f:
        json.dump(user_profile, f, indent=2)
    
    return True, message


def get_connections(user_email: str) -> List[Dict]:
    """Get a user's connections with profile info."""
    profile = get_profile(user_email)
    if not profile:
        return []
    
    connections = []
    for email in profile.get("connections", []):
        conn_profile = get_profile(email)
        if conn_profile:
            connections.append({
                "email": conn_profile["email"],
                "display_name": conn_profile["display_name"],
                "bio": conn_profile.get("bio", "")[:100],
                "preferred_traditions": conn_profile.get("preferred_traditions", []),
                "last_active": conn_profile.get("last_active", ""),
            })
    
    return connections


def get_pending_requests(user_email: str) -> List[Dict]:
    """Get pending connection requests for a user."""
    profile = get_profile(user_email)
    if not profile:
        return []
    
    return profile.get("connection_requests", [])

