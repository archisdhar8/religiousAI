"""
Memory Module for Divine Wisdom Guide

Implements persistent conversation memory so the advisor can remember
past conversations and build a relationship with the seeker.

Supports multiple chat threads (like ChatGPT) with:
- Create new chats
- Switch between chats
- Continue old conversations
- Auto-generate chat titles
"""

import os
import json
import hashlib
import uuid
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


# =====================================================================
# CHAT MANAGEMENT (Multiple Conversations like ChatGPT)
# =====================================================================

def create_new_chat(user_id: str, religion: str = None, title: str = None) -> Dict:
    """
    Create a new chat thread for a user.
    
    Returns:
        The new chat object
    """
    memory = load_user_memory(user_id)
    
    # Initialize chats list if not exists
    if "chats" not in memory:
        memory["chats"] = []
    
    # Generate incremental title if not provided
    if not title:
        # Count existing "New Chat X" titles to determine next number
        existing_numbers = []
        for chat in memory["chats"]:
            chat_title = chat.get("title", "")
            if chat_title.startswith("New Chat "):
                try:
                    num = int(chat_title.replace("New Chat ", ""))
                    existing_numbers.append(num)
                except ValueError:
                    pass
        
        # Find next available number
        next_num = 1
        if existing_numbers:
            next_num = max(existing_numbers) + 1
        
        title = f"New Chat {next_num}"
    
    # Create new chat
    chat_id = str(uuid.uuid4())[:8]
    new_chat = {
        "id": chat_id,
        "title": title,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "religion": religion,
        "messages": []
    }
    
    # Add to beginning of list (most recent first)
    memory["chats"].insert(0, new_chat)
    memory["current_chat_id"] = chat_id
    
    # Limit to 50 chats max
    memory["chats"] = memory["chats"][:50]
    
    save_user_memory(user_id, memory)
    
    return new_chat


def get_chat(user_id: str, chat_id: str) -> Optional[Dict]:
    """Get a specific chat by ID."""
    memory = load_user_memory(user_id)
    
    for chat in memory.get("chats", []):
        if chat["id"] == chat_id:
            return chat
    
    return None


def get_all_chats(user_id: str) -> List[Dict]:
    """
    Get all chats for a user (summary only, not full messages).
    Returns list sorted by most recent.
    """
    memory = load_user_memory(user_id)
    chats = memory.get("chats", [])
    
    # Return summaries only (for sidebar)
    summaries = []
    for chat in chats:
        summaries.append({
            "id": chat["id"],
            "title": chat.get("title", "Untitled"),
            "created_at": chat.get("created_at"),
            "updated_at": chat.get("updated_at"),
            "religion": chat.get("religion"),
            "message_count": len(chat.get("messages", [])),
            "preview": chat["messages"][-1]["content"][:50] + "..." if chat.get("messages") else ""
        })
    
    return summaries


def get_current_chat_id(user_id: str) -> Optional[str]:
    """Get the ID of the user's current active chat."""
    memory = load_user_memory(user_id)
    return memory.get("current_chat_id")


def set_current_chat(user_id: str, chat_id: str) -> bool:
    """Set the current active chat."""
    memory = load_user_memory(user_id)
    
    # Verify chat exists
    chat_exists = any(c["id"] == chat_id for c in memory.get("chats", []))
    if not chat_exists:
        return False
    
    memory["current_chat_id"] = chat_id
    save_user_memory(user_id, memory)
    return True


def add_message_to_chat(
    user_id: str, 
    chat_id: str, 
    role: str, 
    content: str
) -> Optional[Dict]:
    """
    Add a message to a specific chat.
    
    Args:
        user_id: The user's ID
        chat_id: The chat thread ID
        role: "user" or "assistant"
        content: The message content
    
    Returns:
        The updated chat, or None if not found
    """
    memory = load_user_memory(user_id)
    
    for chat in memory.get("chats", []):
        if chat["id"] == chat_id:
            # Add message
            chat["messages"].append({
                "role": role,
                "content": content,
                "timestamp": datetime.now().isoformat()
            })
            chat["updated_at"] = datetime.now().isoformat()
            
            # Auto-generate title from first user message
            if chat["title"] == "New Conversation" and role == "user":
                # Use first 40 chars of first message as title
                chat["title"] = content[:40] + ("..." if len(content) > 40 else "")
            
            # Move this chat to top of list (most recent)
            memory["chats"].remove(chat)
            memory["chats"].insert(0, chat)
            
            save_user_memory(user_id, memory)
            
            # Also update themes for matching
            if role == "user":
                update_themes(memory, content)
                save_user_memory(user_id, memory)
            
            return chat
    
    return None


def get_chat_messages(user_id: str, chat_id: str) -> List[Dict]:
    """Get all messages from a specific chat."""
    chat = get_chat(user_id, chat_id)
    if not chat:
        return []
    return chat.get("messages", [])


def delete_chat(user_id: str, chat_id: str) -> bool:
    """Delete a chat thread."""
    memory = load_user_memory(user_id)
    
    original_count = len(memory.get("chats", []))
    memory["chats"] = [c for c in memory.get("chats", []) if c["id"] != chat_id]
    
    if len(memory["chats"]) < original_count:
        # Chat was deleted
        # If deleted chat was current, set new current
        if memory.get("current_chat_id") == chat_id:
            if memory["chats"]:
                memory["current_chat_id"] = memory["chats"][0]["id"]
            else:
                memory["current_chat_id"] = None
        
        save_user_memory(user_id, memory)
        return True
    
    return False


def rename_chat(user_id: str, chat_id: str, new_title: str) -> bool:
    """Rename a chat thread."""
    memory = load_user_memory(user_id)
    
    for chat in memory.get("chats", []):
        if chat["id"] == chat_id:
            chat["title"] = new_title[:100]  # Limit title length
            save_user_memory(user_id, memory)
            return True
    
    return False


def get_or_create_current_chat(user_id: str, religion: str = None) -> Dict:
    """
    Get the current chat, or create one if none exists.
    Used to ensure there's always an active chat.
    """
    memory = load_user_memory(user_id)
    
    # Check if current chat exists
    current_id = memory.get("current_chat_id")
    if current_id:
        chat = get_chat(user_id, current_id)
        if chat:
            return chat
    
    # Check if any chats exist
    if memory.get("chats") and len(memory["chats"]) > 0:
        # Use first (most recent) chat
        memory["current_chat_id"] = memory["chats"][0]["id"]
        save_user_memory(user_id, memory)
        return memory["chats"][0]
    
    # Create new chat
    return create_new_chat(user_id, religion)


def migrate_old_conversations_to_chats(user_id: str) -> int:
    """
    Migrate old-style conversations to new chat format.
    Returns number of chats created.
    """
    memory = load_user_memory(user_id)
    
    old_convs = memory.get("conversations", [])
    if not old_convs:
        return 0
    
    if "chats" not in memory:
        memory["chats"] = []
    
    migrated = 0
    
    for conv in old_convs:
        # Skip if no exchanges
        exchanges = conv.get("exchanges", [])
        if not exchanges:
            continue
        
        # Create chat from conversation
        chat_id = str(uuid.uuid4())[:8]
        
        # Build messages
        messages = []
        for exchange in exchanges:
            messages.append({
                "role": "user",
                "content": exchange.get("question", ""),
                "timestamp": exchange.get("timestamp", conv.get("date"))
            })
            messages.append({
                "role": "assistant", 
                "content": exchange.get("answer", ""),
                "timestamp": exchange.get("timestamp", conv.get("date"))
            })
        
        # Create title from first question
        title = exchanges[0].get("question", "Conversation")[:40]
        if len(exchanges[0].get("question", "")) > 40:
            title += "..."
        
        chat = {
            "id": chat_id,
            "title": title,
            "created_at": conv.get("date", datetime.now().isoformat()),
            "updated_at": conv.get("date", datetime.now().isoformat()),
            "religion": exchanges[0].get("traditions", [None])[0] if exchanges[0].get("traditions") else None,
            "messages": messages
        }
        
        memory["chats"].append(chat)
        migrated += 1
    
    # Sort by date
    memory["chats"].sort(key=lambda x: x.get("updated_at", ""), reverse=True)
    
    # Set current chat
    if memory["chats"] and not memory.get("current_chat_id"):
        memory["current_chat_id"] = memory["chats"][0]["id"]
    
    # Clear old conversations (optional - keep for backup)
    # memory["conversations"] = []
    
    save_user_memory(user_id, memory)
    
    return migrated


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

