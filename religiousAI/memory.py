"""
Memory Module for Divine Wisdom Guide

Implements persistent conversation memory so the advisor can remember
past conversations and build a relationship with the seeker.
"""

import os
import json
import hashlib
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from config import USER_DATA_DIR


def get_user_id(session_id: str) -> str:
    """Generate a consistent user ID from session info."""
    return hashlib.md5(session_id.encode()).hexdigest()[:12]


def get_user_file(user_id: str) -> str:
    """Get the file path for a user's memory."""
    os.makedirs(USER_DATA_DIR, exist_ok=True)
    return os.path.join(USER_DATA_DIR, f"{user_id}.json")


def load_user_memory(user_id: str) -> Dict:
    """Load a user's memory from disk."""
    filepath = get_user_file(user_id)
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    
    # Return default memory structure
    return {
        "user_id": user_id,
        "created_at": datetime.now().isoformat(),
        "last_visit": datetime.now().isoformat(),
        "visit_count": 0,
        "conversations": [],  # List of {date, exchanges: [{q, a, traditions}]}
        "themes": [],  # Recurring themes/topics
        "journal_entries": [],  # For journal mode
        "preferences": {
            "traditions": [],
            "ui_mode": "standard",
            "ambient_sound": "Silence"
        }
    }


def save_user_memory(user_id: str, memory: Dict) -> None:
    """Save a user's memory to disk."""
    filepath = get_user_file(user_id)
    memory["last_visit"] = datetime.now().isoformat()
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(memory, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving memory: {e}")


def add_exchange(
    memory: Dict, 
    question: str, 
    answer: str, 
    traditions: List[str] = None
) -> Dict:
    """Add a Q&A exchange to memory."""
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Find or create today's conversation
    today_conv = None
    for conv in memory["conversations"]:
        if conv["date"] == today:
            today_conv = conv
            break
    
    if today_conv is None:
        today_conv = {"date": today, "exchanges": []}
        memory["conversations"].append(today_conv)
    
    # Add the exchange
    today_conv["exchanges"].append({
        "timestamp": datetime.now().isoformat(),
        "question": question,
        "answer": answer[:500],  # Truncate for storage
        "traditions": traditions or []
    })
    
    # Keep only last 30 days of conversations
    cutoff = datetime.now().timestamp() - (30 * 24 * 60 * 60)
    memory["conversations"] = [
        c for c in memory["conversations"] 
        if datetime.fromisoformat(c["date"]).timestamp() > cutoff
    ][-30:]  # Also limit to 30 conversations max
    
    # Extract themes (simple keyword extraction)
    update_themes(memory, question)
    
    return memory


def add_journal_entry(memory: Dict, entry: str, reflection: str) -> Dict:
    """Add a journal entry to memory."""
    memory["journal_entries"].append({
        "date": datetime.now().isoformat(),
        "entry": entry[:1000],  # Truncate
        "reflection": reflection[:500]
    })
    
    # Keep only last 30 journal entries
    memory["journal_entries"] = memory["journal_entries"][-30:]
    
    return memory


def update_themes(memory: Dict, text: str) -> None:
    """Extract and update recurring themes from text."""
    # Simple theme keywords (expand as needed)
    theme_keywords = {
        "family": ["family", "mother", "father", "parent", "child", "son", "daughter", "sibling"],
        "grief": ["grief", "loss", "death", "died", "mourning", "passed away", "gone"],
        "forgiveness": ["forgive", "forgiveness", "resentment", "anger", "hurt by"],
        "purpose": ["purpose", "meaning", "lost", "direction", "calling", "destiny"],
        "relationships": ["relationship", "marriage", "partner", "spouse", "friend", "lonely"],
        "anxiety": ["anxious", "anxiety", "worried", "fear", "scared", "nervous"],
        "faith": ["faith", "doubt", "believe", "belief", "trust in god"],
        "gratitude": ["grateful", "thankful", "gratitude", "blessed", "appreciate"],
        "work": ["work", "job", "career", "boss", "coworker", "profession"],
        "health": ["health", "sick", "illness", "disease", "pain", "suffering"],
    }
    
    text_lower = text.lower()
    
    for theme, keywords in theme_keywords.items():
        for keyword in keywords:
            if keyword in text_lower:
                if theme not in memory["themes"]:
                    memory["themes"].append(theme)
                break
    
    # Keep only most recent 10 themes
    memory["themes"] = memory["themes"][-10:]


def get_conversation_summary(memory: Dict, limit: int = 5) -> str:
    """Get a summary of recent conversations for context."""
    if not memory["conversations"]:
        return ""
    
    summaries = []
    exchange_count = 0
    
    # Go through conversations in reverse (most recent first)
    for conv in reversed(memory["conversations"]):
        for exchange in reversed(conv["exchanges"]):
            if exchange_count >= limit:
                break
            summaries.append(
                f"[{conv['date']}] Seeker asked about: {exchange['question'][:100]}..."
            )
            exchange_count += 1
        if exchange_count >= limit:
            break
    
    if not summaries:
        return ""
    
    return "Previous conversations:\n" + "\n".join(reversed(summaries))


def get_themes_summary(memory: Dict) -> str:
    """Get a summary of the seeker's recurring themes."""
    if not memory["themes"]:
        return ""
    
    return f"This seeker often reflects on: {', '.join(memory['themes'])}"


def get_returning_user_greeting(memory: Dict) -> Optional[str]:
    """Generate a personalized greeting for returning users."""
    visit_count = memory.get("visit_count", 0)
    
    if visit_count == 0:
        return None  # New user
    
    themes = memory.get("themes", [])
    last_visit = memory.get("last_visit", "")
    
    try:
        last_date = datetime.fromisoformat(last_visit)
        days_ago = (datetime.now() - last_date).days
    except:
        days_ago = 0
    
    if days_ago == 0:
        time_phrase = "earlier today"
    elif days_ago == 1:
        time_phrase = "yesterday"
    elif days_ago < 7:
        time_phrase = f"{days_ago} days ago"
    else:
        time_phrase = "some time ago"
    
    greeting = f"Welcome back, dear seeker. I remember you were here {time_phrase}."
    
    if themes:
        recent_theme = themes[-1]
        greeting += f" You've been reflecting on matters of {recent_theme}. "
        greeting += "How has your heart been since we last spoke?"
    
    return greeting


def get_context_for_llm(memory: Dict) -> str:
    """
    Generate context string to include in LLM prompt.
    This helps the AI remember and personalize responses.
    """
    parts = []
    
    # Visit info
    visit_count = memory.get("visit_count", 0)
    if visit_count > 1:
        parts.append(f"This is a returning seeker (visit #{visit_count}).")
    
    # Themes
    themes_summary = get_themes_summary(memory)
    if themes_summary:
        parts.append(themes_summary)
    
    # Recent conversations
    conv_summary = get_conversation_summary(memory, limit=3)
    if conv_summary:
        parts.append(conv_summary)
    
    # Journal themes
    if memory.get("journal_entries"):
        recent_journal = memory["journal_entries"][-1]
        parts.append(f"Recent journal reflection: {recent_journal['entry'][:200]}...")
    
    if not parts:
        return ""
    
    return "SEEKER CONTEXT:\n" + "\n".join(parts) + "\n"

