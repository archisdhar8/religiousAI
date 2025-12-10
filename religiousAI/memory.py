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


def get_user_id_from_email(email: str) -> str:
    """Generate a consistent user ID from email address.
    
    This ensures memory persists across logins for authenticated users.
    """
    email_normalized = email.lower().strip()
    return hashlib.md5(email_normalized.encode()).hexdigest()[:12]


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
        "email": None,  # Will be set when linked to account
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
        },
        "personality_traits": {},  # Extracted personality insights
        "spiritual_journey": {  # Track spiritual growth
            "primary_concerns": [],
            "growth_areas": [],
            "milestones": []
        },
        "preferred_wisdom_style": None,  # How user prefers guidance (compassionate, direct, etc.)
        "conversation_summary": ""  # AI-generated summary of user's journey
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
    
    # Extract themes (enhanced keyword extraction)
    update_themes(memory, question)
    
    # Update spiritual journey
    update_spiritual_journey(memory, question, answer)
    
    # Extract personality insights periodically (every 5 exchanges)
    exchange_count = sum(len(conv.get("exchanges", [])) for conv in memory.get("conversations", []))
    if exchange_count % 5 == 0:
        extract_personality_insights(memory)
    
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
    # Enhanced theme keywords (expand as needed)
    theme_keywords = {
        "family": ["family", "mother", "father", "parent", "child", "son", "daughter", "sibling", "brother", "sister"],
        "grief": ["grief", "loss", "death", "died", "mourning", "passed away", "gone", "losing", "lost someone"],
        "forgiveness": ["forgive", "forgiveness", "resentment", "anger", "hurt by", "betrayed", "wronged"],
        "purpose": ["purpose", "meaning", "lost", "direction", "calling", "destiny", "why am i here", "what is my purpose"],
        "relationships": ["relationship", "marriage", "partner", "spouse", "friend", "lonely", "dating", "breakup"],
        "anxiety": ["anxious", "anxiety", "worried", "fear", "scared", "nervous", "panic", "overwhelmed"],
        "faith": ["faith", "doubt", "believe", "belief", "trust in god", "questioning", "spiritual doubt"],
        "gratitude": ["grateful", "thankful", "gratitude", "blessed", "appreciate", "thankful for"],
        "work": ["work", "job", "career", "boss", "coworker", "profession", "employment", "colleague"],
        "health": ["health", "sick", "illness", "disease", "pain", "suffering", "medical", "treatment"],
        "guilt": ["guilt", "guilty", "shame", "ashamed", "regret", "remorse", "sin", "wrongdoing"],
        "loneliness": ["lonely", "alone", "isolated", "no one", "nobody", "empty", "disconnected"],
        "hope": ["hope", "hopeful", "optimistic", "future", "better", "improve", "healing"],
        "peace": ["peace", "calm", "serenity", "tranquil", "inner peace", "stillness"],
    }
    
    text_lower = text.lower()
    
    for theme, keywords in theme_keywords.items():
        for keyword in keywords:
            if keyword in text_lower:
                if theme not in memory["themes"]:
                    memory["themes"].append(theme)
                break
    
    # Keep only most recent 15 themes (increased from 10)
    memory["themes"] = memory["themes"][-15:]


def extract_personality_insights(memory: Dict) -> Dict:
    """
    Extract personality insights from conversation history.
    This is a simple rule-based approach. For deeper analysis, could use LLM.
    """
    traits = {}
    
    # Analyze conversation patterns
    all_questions = []
    for conv in memory.get("conversations", []):
        for exchange in conv.get("exchanges", []):
            all_questions.append(exchange.get("question", "").lower())
    
    if not all_questions:
        return traits
    
    combined_text = " ".join(all_questions)
    
    # Emotional patterns
    if any(word in combined_text for word in ["anxious", "worried", "fear", "scared"]):
        traits["emotional_state"] = "tends to experience anxiety"
    elif any(word in combined_text for word in ["grateful", "thankful", "blessed"]):
        traits["emotional_state"] = "expresses gratitude frequently"
    elif any(word in combined_text for word in ["sad", "depressed", "down", "hopeless"]):
        traits["emotional_state"] = "may be experiencing sadness"
    else:
        traits["emotional_state"] = "seeking guidance"
    
    # Communication style
    question_lengths = [len(q) for q in all_questions]
    avg_length = sum(question_lengths) / len(question_lengths) if question_lengths else 0
    
    if avg_length > 100:
        traits["communication_style"] = "detailed and expressive"
    elif avg_length < 30:
        traits["communication_style"] = "concise and direct"
    else:
        traits["communication_style"] = "balanced"
    
    # Question patterns
    if any("?" in q for q in all_questions[:5]):
        if sum(1 for q in all_questions[:5] if "?" in q) >= 3:
            traits["inquiry_style"] = "asks many questions"
        else:
            traits["inquiry_style"] = "asks thoughtful questions"
    
    # Update memory with traits
    memory["personality_traits"] = traits
    
    return traits


def update_spiritual_journey(memory: Dict, question: str, answer: str) -> None:
    """
    Update spiritual journey tracking based on conversations.
    """
    journey = memory.setdefault("spiritual_journey", {
        "primary_concerns": [],
        "growth_areas": [],
        "milestones": []
    })
    
    # Extract primary concerns from themes
    themes = memory.get("themes", [])
    for theme in themes:
        if theme not in journey["primary_concerns"]:
            journey["primary_concerns"].append(theme)
            # Keep only top 5 concerns
            journey["primary_concerns"] = journey["primary_concerns"][-5:]
    
    # Identify growth areas (themes that appear frequently)
    theme_counts = {}
    for conv in memory.get("conversations", []):
        for exchange in conv.get("exchanges", []):
            for theme in themes:
                if theme in exchange.get("question", "").lower():
                    theme_counts[theme] = theme_counts.get(theme, 0) + 1
    
    # Top 3 most discussed themes become growth areas
    if theme_counts:
        sorted_themes = sorted(theme_counts.items(), key=lambda x: x[1], reverse=True)
        journey["growth_areas"] = [theme for theme, _ in sorted_themes[:3]]
    
    # Detect milestones (significant shifts in themes or visit count)
    visit_count = memory.get("visit_count", 0)
    if visit_count > 0 and visit_count % 10 == 0:
        milestone = f"Completed {visit_count} conversations"
        if milestone not in journey["milestones"]:
            journey["milestones"].append(milestone)
            journey["milestones"] = journey["milestones"][-10:]  # Keep last 10 milestones


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
    
    # Personality traits
    personality = memory.get("personality_traits", {})
    if personality:
        traits_list = [f"{k}: {v}" for k, v in personality.items() if v]
        if traits_list:
            parts.append(f"Personality insights: {', '.join(traits_list)}")
    
    # Preferred wisdom style
    wisdom_style = memory.get("preferred_wisdom_style")
    if wisdom_style:
        parts.append(f"This seeker prefers {wisdom_style} guidance.")
    
    # Spiritual journey
    journey = memory.get("spiritual_journey", {})
    if journey.get("primary_concerns"):
        concerns = ", ".join(journey["primary_concerns"][:3])
        parts.append(f"Primary concerns: {concerns}")
    if journey.get("growth_areas"):
        growth = ", ".join(journey["growth_areas"][:3])
        parts.append(f"Areas of growth: {growth}")
    
    # Themes
    themes_summary = get_themes_summary(memory)
    if themes_summary:
        parts.append(themes_summary)
    
    # Recent conversations
    conv_summary = get_conversation_summary(memory, limit=3)
    if conv_summary:
        parts.append(conv_summary)
    
    # Conversation summary (if available)
    if memory.get("conversation_summary"):
        parts.append(f"Journey summary: {memory['conversation_summary'][:300]}...")
    
    # Journal themes
    if memory.get("journal_entries"):
        recent_journal = memory["journal_entries"][-1]
        parts.append(f"Recent journal reflection: {recent_journal['entry'][:200]}...")
    
    if not parts:
        return ""
    
    return "SEEKER CONTEXT:\n" + "\n".join(parts) + "\n"


def migrate_session_memory_to_account(session_id: str, email: str) -> bool:
    """
    Migrate session-based memory to account-based memory.
    
    Args:
        session_id: The session ID to migrate from
        email: The email address to migrate to
    
    Returns:
        True if migration successful, False otherwise
    """
    try:
        session_user_id = get_user_id(session_id)
        account_user_id = get_user_id_from_email(email)
        
        # If they're the same, no migration needed
        if session_user_id == account_user_id:
            return True
        
        session_memory_file = get_user_file(session_user_id)
        account_memory_file = get_user_file(account_user_id)
        
        # Load session memory
        session_memory = None
        if os.path.exists(session_memory_file):
            try:
                with open(session_memory_file, 'r', encoding='utf-8') as f:
                    session_memory = json.load(f)
            except:
                pass
        
        # If no session memory, nothing to migrate
        if not session_memory:
            return True
        
        # Load or create account memory
        account_memory = load_user_memory(account_user_id)
        
        # Merge memories
        # Link email to account memory
        account_memory["email"] = email.lower().strip()
        
        # Merge conversations (keep unique dates)
        session_convs = {c["date"]: c for c in session_memory.get("conversations", [])}
        account_convs = {c["date"]: c for c in account_memory.get("conversations", [])}
        account_convs.update(session_convs)
        account_memory["conversations"] = list(account_convs.values())
        
        # Merge themes (keep unique)
        session_themes = set(session_memory.get("themes", []))
        account_themes = set(account_memory.get("themes", []))
        account_memory["themes"] = list(account_themes.union(session_themes))[-10:]
        
        # Merge journal entries (keep most recent)
        all_journals = account_memory.get("journal_entries", []) + session_memory.get("journal_entries", [])
        # Sort by date and keep most recent 30
        all_journals.sort(key=lambda x: x.get("date", ""), reverse=True)
        account_memory["journal_entries"] = all_journals[:30]
        
        # Use earlier created_at if session memory is older
        try:
            session_created = datetime.fromisoformat(session_memory.get("created_at", ""))
            account_created = datetime.fromisoformat(account_memory.get("created_at", ""))
            if session_created < account_created:
                account_memory["created_at"] = session_memory["created_at"]
        except:
            pass
        
        # Save merged memory
        save_user_memory(account_user_id, account_memory)
        
        # Optionally delete session memory file (or keep as backup)
        # Uncomment to delete:
        # try:
        #     os.unlink(session_memory_file)
        # except:
        #     pass
        
        return True
    except Exception as e:
        print(f"Error migrating memory: {e}")
        return False

