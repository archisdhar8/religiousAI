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
    load_user_memory,
    save_user_memory,
    add_exchange,
    add_journal_entry,
    get_returning_user_greeting
)
from config import TRADITIONS, ADVISOR_GREETING

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

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://127.0.0.1:8080"],
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


class TraditionsResponse(BaseModel):
    traditions: List[Dict[str, str]]


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
        # Get user memory
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
        # Get user memory
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
async def get_greeting(session_id: Optional[str] = None):
    """Get personalized greeting for returning users."""
    try:
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

