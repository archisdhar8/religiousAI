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
    get_available_traditions,
    compare_traditions,
    generate_daily_wisdom,
    generate_journal_reflection
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


class ChatResponse(BaseModel):
    response: str
    is_crisis: bool
    sources: Optional[List[Dict]] = None


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


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"message": "Divine Wisdom Guide API", "status": "running"}


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
    """Process a chat message and return spiritual guidance."""
    try:
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
        
        # Ask question
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
            sources=sources
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
    """Compare how different traditions approach a topic."""
    try:
        # Ensure tradition names are correct
        valid_traditions = [t for t in request.traditions if t in TRADITIONS]
        if len(valid_traditions) < 2:
            raise HTTPException(
                status_code=400,
                detail="Please provide at least 2 valid traditions to compare"
            )
        
        comparison, docs = compare_traditions(request.topic, valid_traditions)
        
        # Format sources
        sources = {}
        for tradition, tradition_docs in docs.items():
            sources[tradition] = [
                {
                    "scripture": doc.metadata.get("scripture_name", "Unknown"),
                    "content": doc.page_content[:300] + "..." if len(doc.page_content) > 300 else doc.page_content
                }
                for doc in tradition_docs
            ]
        
        return {
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

