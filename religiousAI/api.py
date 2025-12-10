"""
FastAPI REST API Server for Divine Wisdom Guide

Exposes the backend functionality as REST endpoints for the React frontend.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
import uuid

from qa import (
    ask_question,
    ask_question_multi_agent,
    get_available_traditions,
    compare_traditions,
    generate_daily_wisdom,
    generate_journal_reflection,
    MULTI_AGENT_AVAILABLE
)
from memory import (
    get_user_id,
    get_user_id_from_email,
    load_user_memory,
    save_user_memory,
    add_exchange,
    add_journal_entry,
    get_returning_user_greeting,
    migrate_session_memory_to_account
)
from config import TRADITIONS, ADVISOR_GREETING
from auth import (
    create_user,
    authenticate_user,
    create_session,
    validate_session,
    delete_session,
    get_user_by_email,
    update_user_preferences
)
from community import (
    create_or_update_profile,
    get_profile,
    find_matches,
    send_connection_request,
    respond_to_request,
    get_connections,
    get_pending_requests,
    extract_traits_from_themes
)

# Frontend religion IDs to backend tradition names mapping
RELIGION_TO_TRADITION = {
    "christianity": "Christianity",
    "islam": "Islam",
    "judaism": "Judaism",
    "hinduism": "Hinduism",
    "buddhism": "Buddhism",
    "sikhism": "Sikhism",
    "taoism": "Taoism",
    "shinto": "Shinto",  # Note: Shinto may not be in backend, will handle gracefully
}

app = FastAPI(title="Divine Wisdom Guide API", version="1.0.0")

# CORS middleware - Allow localhost and local network IPs
# For production, replace with specific allowed origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8080",
        "http://127.0.0.1:8080",
        "http://192.168.1.200:8080",  # Allow local network IP
        "http://localhost:5173",  # Vite default port
        "http://127.0.0.1:5173",
        # Allow any local network IP on port 8080 (for development)
        # Pattern: http://192.168.*.*:8080, http://10.*.*.*:8080, http://172.16-31.*.*:8080
    ],
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1|192\.168\.\d+\.\d+|10\.\d+\.\d+\.\d+|172\.(1[6-9]|2[0-9]|3[0-1])\.\d+\.\d+):(8080|5173)",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response Models
class ChatRequest(BaseModel):
    message: str
    religion: Optional[str] = None  # Frontend religion ID
    session_id: Optional[str] = None
    conversation_history: Optional[List[Dict[str, str]]] = None
    mode: str = "standard"
    use_multi_agent: bool = False  # Enable multi-agent system
    authorization: Optional[str] = None  # Bearer token for authenticated users


class ChatResponse(BaseModel):
    response: str
    is_crisis: bool
    sources: Optional[List[Dict]] = None
    agent_outputs: Optional[Dict[str, str]] = None  # Individual agent responses (for transparency)


class DailyWisdomResponse(BaseModel):
    wisdom: str
    tradition: str
    scripture: str


class CompareRequest(BaseModel):
    topic: str
    traditions: List[str]


class JournalRequest(BaseModel):
    entry: str
    session_id: Optional[str] = None
    authorization: Optional[str] = None  # Bearer token for authenticated users


class TraditionsResponse(BaseModel):
    traditions: List[Dict[str, str]]


# Auth Models
class SignUpRequest(BaseModel):
    email: str
    password: str
    name: Optional[str] = None


class LoginRequest(BaseModel):
    email: str
    password: str


class AuthResponse(BaseModel):
    success: bool
    message: str
    token: Optional[str] = None
    user: Optional[Dict] = None


class UserResponse(BaseModel):
    email: str
    name: str
    created_at: str
    preferences: Dict


def get_tradition_from_religion(religion_id: Optional[str]) -> Optional[List[str]]:
    """Convert frontend religion ID to backend tradition name(s)."""
    if not religion_id:
        return None
    
    tradition = RELIGION_TO_TRADITION.get(religion_id.lower())
    if tradition:
        # Check if tradition exists in backend
        if tradition in TRADITIONS:
            return [tradition]
    
    return None


def detect_comparison_request(message: str) -> tuple[bool, Optional[str], Optional[List[str]]]:
    """
    Detect if user is asking for a cross-religious comparison.
    
    Returns:
        (is_comparison, topic, traditions_to_compare)
    """
    message_lower = message.lower()
    
    # Patterns that indicate comparison requests
    comparison_patterns = [
        "compare",
        "what does christianity say" and "what about",
        "what does islam say" and "what about", 
        "what does buddhism say" and "what about",
        "how do different",
        "different religions",
        "different faiths",
        "across traditions",
        "across religions",
        "various religions",
        "multiple faiths",
    ]
    
    is_comparison = any(pattern in message_lower for pattern in comparison_patterns)
    
    # Also check for pattern: "What does X say about Y? What about Z?"
    if "what does" in message_lower and "what about" in message_lower:
        is_comparison = True
    
    if not is_comparison:
        return False, None, None
    
    # Extract which traditions are mentioned
    mentioned_traditions = []
    tradition_keywords = {
        "christianity": "Christianity", "christian": "Christianity", "bible": "Christianity",
        "islam": "Islam", "muslim": "Islam", "quran": "Islam",
        "buddhism": "Buddhism", "buddhist": "Buddhism", "buddha": "Buddhism",
        "hinduism": "Hinduism", "hindu": "Hinduism", "gita": "Hinduism",
        "judaism": "Judaism", "jewish": "Judaism", "torah": "Judaism",
        "taoism": "Taoism", "taoist": "Taoism", "tao": "Taoism",
        "sikhism": "Sikhism", "sikh": "Sikhism",
        "stoicism": "Stoicism", "stoic": "Stoicism",
        "confucianism": "Confucianism", "confucian": "Confucianism",
    }
    
    for keyword, tradition in tradition_keywords.items():
        if keyword in message_lower and tradition not in mentioned_traditions:
            mentioned_traditions.append(tradition)
    
    # If no specific traditions mentioned, use defaults
    if len(mentioned_traditions) < 2:
        mentioned_traditions = ["Christianity", "Islam", "Buddhism", "Hinduism"]
    
    # Extract topic (simplified - take the main subject)
    # Remove comparison words to get the topic
    topic = message
    for word in ["compare", "what does", "say about", "what about", "how do", "different religions", "view"]:
        topic = topic.lower().replace(word, "")
    topic = topic.strip().strip("?").strip()
    
    # If topic is too short, use the original message
    if len(topic) < 3:
        topic = message
    
    return True, topic, mentioned_traditions


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "message": "Divine Wisdom Guide API", 
        "status": "running",
        "multi_agent_available": MULTI_AGENT_AVAILABLE,
        "features": [
            "chat",
            "multi-agent-chat",
            "compare-religions",
            "daily-wisdom",
            "journal"
        ]
    }


@app.get("/api/traditions", response_model=TraditionsResponse)
async def get_traditions():
    """Get available traditions with their metadata."""
    traditions_list = []
    for key, value in TRADITIONS.items():
        traditions_list.append({
            "id": key.lower(),
            "name": key,
            "icon": value.get("icon", "📖"),
            "description": value.get("description", "")
        })
    
    return TraditionsResponse(traditions=traditions_list)


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Process a chat message and return spiritual guidance.
    
    Features:
    - Auto-detects cross-religious comparison requests
    - Set use_multi_agent=True for the 4-agent system
    
    Multi-agent system uses:
    - Compassion Agent (emotional grounding)
    - Scripture Agent (accurate citations)
    - Scholar Agent (theological interpretation)
    - Guidance Agent (practical advice)
    """
    try:
        # Check if this is a comparison request
        is_comparison, topic, compare_traditions_list = detect_comparison_request(request.message)
        
        if is_comparison and compare_traditions_list:
            # Route to comparison logic
            comparison_result, docs = compare_traditions(topic, compare_traditions_list)
            
            # Format sources from comparison
            sources = []
            if isinstance(docs, dict):
                for tradition, tradition_docs in docs.items():
                    for doc in tradition_docs:
                        sources.append({
                            "tradition": tradition,
                            "scripture": doc.metadata.get("scripture_name", "Unknown"),
                            "content": doc.page_content[:300] + "..."
                        })
            
            return ChatResponse(
                response=comparison_result,
                is_crisis=False,
                sources=sources,
                agent_outputs={"mode": "cross-religious-comparison", "traditions": compare_traditions_list}
            )
        
        # Regular chat flow
        # Get user memory - use email-based ID if authenticated, otherwise session-based
        user_email = None
        user_id = None
        
        # Check if user is authenticated via authorization header
        try:
            if request.authorization:
                user_email = get_email_from_auth(request.authorization)
                if user_email:
                    # Use email-based user ID for authenticated users
                    user_id = get_user_id_from_email(user_email)
                    # Link email to memory if not already linked
                    user_memory = load_user_memory(user_id)
                    if not user_memory.get("email"):
                        user_memory["email"] = user_email
                        save_user_memory(user_id, user_memory)
        except HTTPException:
            # Invalid token, fall back to session-based
            pass
        
        # If not authenticated or auth failed, use session-based ID
        if not user_id:
            session_id = request.session_id or str(uuid.uuid4())
            user_id = get_user_id(session_id)
            user_memory = load_user_memory(user_id)
        
        user_memory["visit_count"] = user_memory.get("visit_count", 0) + 1
        
        # Convert religion to tradition
        traditions = get_tradition_from_religion(request.religion)
        
        # Convert conversation history format
        conversation_history = None
        if request.conversation_history:
            conversation_history = [
                (item.get("question", ""), item.get("answer", ""))
                for item in request.conversation_history
            ]
        
        # Get message count from memory
        message_count = sum(
            len(conv.get("exchanges", []))
            for conv in user_memory.get("conversations", [])
        )
        
        # Choose single-agent or multi-agent based on request
        agent_outputs = None
        
        if request.use_multi_agent and MULTI_AGENT_AVAILABLE:
            # Use multi-agent system (4 specialized agents)
            response_text, docs, is_crisis, agent_outputs = ask_question_multi_agent(
                question=request.message,
                traditions=traditions,
                conversation_history=conversation_history,
                user_memory=user_memory,
                message_count=message_count
            )
        else:
            # Use standard single-agent
            response_text, docs, is_crisis = ask_question(
                question=request.message,
                traditions=traditions,
                conversation_history=conversation_history,
                user_memory=user_memory,
                mode=request.mode,
                message_count=message_count
            )
        
        # Format sources
        sources = None
        if docs and not is_crisis:
            sources = [
                {
                    "tradition": doc.metadata.get("tradition", "Unknown"),
                    "scripture": doc.metadata.get("scripture_name", doc.metadata.get("book_title", "Unknown")),
                    "content": doc.page_content[:300] + "..." if len(doc.page_content) > 300 else doc.page_content
                }
                for doc in docs
            ]
        
        # Save to memory if not crisis
        if not is_crisis:
            user_memory = add_exchange(
                user_memory,
                request.message,
                response_text,
                traditions
            )
            save_user_memory(user_id, user_memory)
        
        return ChatResponse(
            response=response_text,
            is_crisis=is_crisis,
            sources=sources,
            agent_outputs=agent_outputs
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")


@app.get("/api/daily-wisdom", response_model=DailyWisdomResponse)
async def daily_wisdom(session_id: Optional[str] = None, religion: Optional[str] = None):
    """Get daily wisdom quote."""
    try:
        # Get user memory for themes
        user_memory = None
        if session_id:
            user_id = get_user_id(session_id)
            user_memory = load_user_memory(user_id)
        
        themes = user_memory.get("themes", []) if user_memory else None
        traditions = get_tradition_from_religion(religion)
        
        wisdom, tradition, scripture = generate_daily_wisdom(
            user_themes=themes,
            traditions=traditions
        )
        
        return DailyWisdomResponse(
            wisdom=wisdom,
            tradition=tradition,
            scripture=scripture or ""
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating daily wisdom: {str(e)}")


@app.post("/api/compare")
async def compare(request: CompareRequest):
    """
    Compare how different traditions approach a topic.
    
    Example request:
    {
        "topic": "forgiveness",
        "traditions": ["Christianity", "Islam", "Buddhism"]
    }
    
    Returns a respectful comparison with cited scriptures from each tradition.
    """
    try:
        # Ensure tradition names are correct (case-insensitive matching)
        valid_traditions = []
        for t in request.traditions:
            # Try exact match first
            if t in TRADITIONS:
                valid_traditions.append(t)
            else:
                # Try case-insensitive match
                for tradition_name in TRADITIONS.keys():
                    if tradition_name.lower() == t.lower():
                        valid_traditions.append(tradition_name)
                        break
        
        if len(valid_traditions) < 2:
            available = list(TRADITIONS.keys())
            raise HTTPException(
                status_code=400,
                detail=f"Please provide at least 2 valid traditions. Available: {available}"
            )
        
        comparison, docs = compare_traditions(request.topic, valid_traditions)
        
        # Format sources by tradition
        sources = {}
        for tradition, tradition_docs in docs.items():
            icon = TRADITIONS.get(tradition, {}).get("icon", "📖")
            sources[tradition] = {
                "icon": icon,
                "passages": [
                    {
                        "scripture": doc.metadata.get("scripture_name", "Unknown"),
                        "content": doc.page_content[:400] + "..." if len(doc.page_content) > 400 else doc.page_content
                    }
                    for doc in tradition_docs
                ]
            }
        
        return {
            "topic": request.topic,
            "traditions_compared": valid_traditions,
            "comparison": comparison,
            "sources": sources
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error comparing traditions: {str(e)}")


@app.post("/api/journal")
async def journal(request: JournalRequest):
    """Generate a reflection on a journal entry."""
    try:
        # Get user memory - use email-based ID if authenticated, otherwise session-based
        user_email = None
        user_id = None
        
        # Check if user is authenticated via authorization header
        try:
            if request.authorization:
                user_email = get_email_from_auth(request.authorization)
                if user_email:
                    # Use email-based user ID for authenticated users
                    user_id = get_user_id_from_email(user_email)
                    # Link email to memory if not already linked
                    user_memory = load_user_memory(user_id)
                    if not user_memory.get("email"):
                        user_memory["email"] = user_email
                        save_user_memory(user_id, user_memory)
        except HTTPException:
            # Invalid token, fall back to session-based
            pass
        
        # If not authenticated or auth failed, use session-based ID
        if not user_id:
            session_id = request.session_id or str(uuid.uuid4())
            user_id = get_user_id(session_id)
            user_memory = load_user_memory(user_id)
        
        # Generate reflection
        reflection = generate_journal_reflection(request.entry, user_memory)
        
        # Save journal entry
        user_memory = add_journal_entry(user_memory, request.entry, reflection)
        save_user_memory(user_id, user_memory)
        
        return {
            "reflection": reflection
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing journal entry: {str(e)}")


@app.get("/api/user/{user_id}")
async def get_user(user_id: str):
    """Get user memory data."""
    try:
        memory = load_user_memory(user_id)
        # Don't return full memory, just summary
        return {
            "user_id": user_id,
            "visit_count": memory.get("visit_count", 0),
            "themes": memory.get("themes", []),
            "has_history": len(memory.get("conversations", [])) > 0
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading user: {str(e)}")


@app.get("/api/greeting")
async def get_greeting(session_id: Optional[str] = None, authorization: Optional[str] = None):
    """Get personalized greeting for returning users."""
    try:
        user_id = None
        
        # Check if user is authenticated via authorization header
        try:
            if authorization:
                user_email = get_email_from_auth(authorization)
                if user_email:
                    # Use email-based user ID for authenticated users
                    user_id = get_user_id_from_email(user_email)
        except HTTPException:
            # Invalid token, fall back to session-based
            pass
        
        # If not authenticated or auth failed, use session-based ID
        if not user_id:
            if not session_id:
                return {"greeting": ADVISOR_GREETING}
            user_id = get_user_id(session_id)
        
        user_memory = load_user_memory(user_id)
        greeting = get_returning_user_greeting(user_memory)
        
        return {
            "greeting": greeting or ADVISOR_GREETING
        }
    except Exception as e:
        return {"greeting": ADVISOR_GREETING}


@app.post("/api/migrate-memory")
async def migrate_memory(authorization: Optional[str] = None, session_id: Optional[str] = None):
    """
    Migrate session-based memory to account-based memory.
    
    This endpoint should be called after a user logs in to migrate their
    session-based memory to their account-based memory.
    """
    try:
        if not authorization:
            raise HTTPException(status_code=401, detail="Authentication required for migration")
        
        # Get user email from auth token
        user_email = get_email_from_auth(authorization)
        
        if not session_id:
            raise HTTPException(status_code=400, detail="session_id required for migration")
        
        # Perform migration
        success = migrate_session_memory_to_account(session_id, user_email)
        
        if success:
            return {
                "success": True,
                "message": "Memory migrated successfully"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to migrate memory")
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error migrating memory: {str(e)}")


# =====================================================================
# AUTHENTICATION ENDPOINTS
# =====================================================================

@app.post("/api/auth/signup", response_model=AuthResponse)
async def signup(request: SignUpRequest):
    """
    Create a new user account.
    """
    try:
        # Normalize email and handle empty name
        email = request.email.lower().strip() if request.email else ""
        name = request.name.strip() if request.name and request.name.strip() else None
        
        if not email:
            raise HTTPException(status_code=400, detail="Email is required")
        
        if not request.password:
            raise HTTPException(status_code=400, detail="Password is required")
        
        success, message = create_user(
            email=email,
            password=request.password,
            name=name
        )
        
        if success:
            # Auto-login after signup
            token = create_session(email)
            user = get_user_by_email(email)
            
            if not user:
                raise HTTPException(
                    status_code=500, 
                    detail="Account created but failed to retrieve user data. Please try logging in."
                )
            
            return AuthResponse(
                success=True,
                message=message,
                token=token,
                user=user
            )
        else:
            raise HTTPException(status_code=400, detail=message)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during signup: {str(e)}")


@app.post("/api/auth/login", response_model=AuthResponse)
async def login(request: LoginRequest):
    """
    Login with email and password.
    """
    try:
        # Normalize email
        email = request.email.lower().strip() if request.email else ""
        
        if not email:
            raise HTTPException(status_code=400, detail="Email is required")
        
        if not request.password:
            raise HTTPException(status_code=400, detail="Password is required")
        
        success, message, user = authenticate_user(
            email=email,
            password=request.password
        )
        
        if success:
            if not user:
                raise HTTPException(
                    status_code=500,
                    detail="Authentication succeeded but failed to retrieve user data."
                )
            
            token = create_session(email)
            return AuthResponse(
                success=True,
                message=message,
                token=token,
                user=user
            )
        else:
            raise HTTPException(status_code=401, detail=message)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during login: {str(e)}")


@app.post("/api/auth/logout")
async def logout(token: Optional[str] = None):
    """
    Logout and invalidate session.
    """
    if token:
        delete_session(token)
    return {"success": True, "message": "Logged out successfully"}


@app.get("/api/auth/me")
async def get_current_user(authorization: Optional[str] = None):
    """
    Get current user info from session token.
    Pass token in Authorization header as 'Bearer <token>'
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Extract token from "Bearer <token>"
    token = authorization.replace("Bearer ", "") if authorization.startswith("Bearer ") else authorization
    
    is_valid, email = validate_session(token)
    
    if not is_valid or not email:
        raise HTTPException(status_code=401, detail="Invalid or expired session")
    
    user = get_user_by_email(email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user


@app.put("/api/auth/preferences")
async def update_preferences(
    preferences: Dict,
    authorization: Optional[str] = None
):
    """
    Update user preferences.
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    token = authorization.replace("Bearer ", "") if authorization.startswith("Bearer ") else authorization
    is_valid, email = validate_session(token)
    
    if not is_valid or not email:
        raise HTTPException(status_code=401, detail="Invalid or expired session")
    
    success = update_user_preferences(email, preferences)
    if success:
        return {"success": True, "message": "Preferences updated"}
    else:
        raise HTTPException(status_code=500, detail="Failed to update preferences")


# =====================================================================
# COMMUNITY ENDPOINTS
# =====================================================================

class CommunityProfileRequest(BaseModel):
    display_name: str
    bio: Optional[str] = None
    preferred_traditions: Optional[List[str]] = None
    opt_in: bool = True


class ConnectionRequest(BaseModel):
    to_email: str
    message: Optional[str] = ""


class ConnectionResponseRequest(BaseModel):
    from_email: str
    accept: bool


def get_email_from_auth(authorization: Optional[str]) -> str:
    """Helper to extract email from auth token."""
    if not authorization:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    token = authorization.replace("Bearer ", "") if authorization.startswith("Bearer ") else authorization
    is_valid, email = validate_session(token)
    
    if not is_valid or not email:
        raise HTTPException(status_code=401, detail="Invalid or expired session")
    
    return email


@app.post("/api/community/profile")
async def create_community_profile(
    request: CommunityProfileRequest,
    authorization: Optional[str] = None
):
    """
    Create or update community profile for matching.
    AI will analyze your conversations to find compatible spiritual companions.
    """
    email = get_email_from_auth(authorization)
    
    # Get user's conversation themes for trait extraction
    user_id = get_user_id(email)
    user_memory = load_user_memory(user_id)
    
    themes = user_memory.get("themes", [])
    conversations = user_memory.get("conversations", [])
    
    # Extract traits from conversation history
    traits = extract_traits_from_themes(themes, conversations)
    
    # Add preferred traditions to traits
    if request.preferred_traditions:
        traits["preferred_traditions"] = request.preferred_traditions
    
    profile = create_or_update_profile(
        user_email=email,
        display_name=request.display_name,
        bio=request.bio,
        traits=traits,
        preferred_traditions=request.preferred_traditions,
        opt_in=request.opt_in
    )
    
    return {
        "success": True,
        "profile": {
            "display_name": profile["display_name"],
            "bio": profile["bio"],
            "traits": profile["traits"],
            "preferred_traditions": profile["preferred_traditions"],
            "opt_in": profile["opt_in"]
        }
    }


@app.get("/api/community/profile")
async def get_community_profile(authorization: Optional[str] = None):
    """Get current user's community profile."""
    email = get_email_from_auth(authorization)
    
    profile = get_profile(email)
    if not profile:
        return {"profile": None}
    
    return {
        "profile": {
            "display_name": profile["display_name"],
            "bio": profile.get("bio", ""),
            "traits": profile.get("traits", {}),
            "preferred_traditions": profile.get("preferred_traditions", []),
            "opt_in": profile.get("opt_in", True),
            "connections_count": len(profile.get("connections", [])),
            "pending_requests": len(profile.get("connection_requests", []))
        }
    }


@app.get("/api/community/matches")
async def get_matches(
    limit: int = 10,
    authorization: Optional[str] = None
):
    """
    Find compatible spiritual companions based on conversation themes,
    struggles, and faith interests.
    """
    email = get_email_from_auth(authorization)
    
    profile = get_profile(email)
    if not profile:
        raise HTTPException(
            status_code=400, 
            detail="Please create a community profile first"
        )
    
    if not profile.get("opt_in"):
        raise HTTPException(
            status_code=400,
            detail="Please opt-in to community matching in your profile"
        )
    
    matches = find_matches(email, limit=limit)
    
    return {
        "matches": matches,
        "total": len(matches)
    }


@app.post("/api/community/connect")
async def request_connection(
    request: ConnectionRequest,
    authorization: Optional[str] = None
):
    """Send a connection request to another user."""
    email = get_email_from_auth(authorization)
    
    success, message = send_connection_request(
        from_email=email,
        to_email=request.to_email,
        message=request.message or ""
    )
    
    if not success:
        raise HTTPException(status_code=400, detail=message)
    
    return {"success": True, "message": message}


@app.post("/api/community/respond")
async def respond_connection(
    request: ConnectionResponseRequest,
    authorization: Optional[str] = None
):
    """Accept or decline a connection request."""
    email = get_email_from_auth(authorization)
    
    success, message = respond_to_request(
        user_email=email,
        from_email=request.from_email,
        accept=request.accept
    )
    
    if not success:
        raise HTTPException(status_code=400, detail=message)
    
    return {"success": True, "message": message}


@app.get("/api/community/connections")
async def list_connections(authorization: Optional[str] = None):
    """Get list of connected spiritual companions."""
    email = get_email_from_auth(authorization)
    
    connections = get_connections(email)
    
    return {
        "connections": connections,
        "total": len(connections)
    }


@app.get("/api/community/requests")
async def list_requests(authorization: Optional[str] = None):
    """Get pending connection requests."""
    email = get_email_from_auth(authorization)
    
    requests = get_pending_requests(email)
    
    return {
        "requests": requests,
        "total": len(requests)
    }
