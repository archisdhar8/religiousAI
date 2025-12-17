"""
Memory Module for Divine Wisdom Guide - Supabase Implementation

Implements persistent conversation memory using Supabase database.
Falls back to file-based storage if USE_SUPABASE is False.
"""

import os
import json
import hashlib
import uuid
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from config import USER_DATA_DIR, USE_SUPABASE
from supabase_client import get_supabase_client

# Import LLM for title generation
try:
    from qa import generate_with_llm
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False


# =====================================================================
# USER ID HELPERS
# =====================================================================

def get_user_id(session_id: str) -> str:
    """
    Generate a consistent user ID from session info.
    For Supabase, this returns a UUID-like string that can be mapped to auth.users.
    For file-based, returns MD5 hash.
    """
    if USE_SUPABASE:
        # For Supabase, we'll need to map session_id to user_id
        # This is a temporary ID until user authenticates
        return hashlib.md5(session_id.encode()).hexdigest()[:12]
    else:
        return hashlib.md5(session_id.encode()).hexdigest()[:12]


def get_user_id_from_email(email: str) -> str:
    """
    Get user ID from email address.
    For Supabase, this should return the UUID from auth.users.
    For file-based, returns MD5 hash.
    """
    email_normalized = email.lower().strip()
    
    if USE_SUPABASE:
        try:
            supabase = get_supabase_client(use_service_role=False)
            response = supabase.table("users").select("id").eq("email", email_normalized).execute()
            if response.data and len(response.data) > 0:
                return response.data[0]["id"]
        except:
            pass
        
        # Fallback to hash if user not found
        return hashlib.md5(email_normalized.encode()).hexdigest()[:12]
    else:
        return hashlib.md5(email_normalized.encode()).hexdigest()[:12]


def _get_supabase_user_id(user_id: str) -> Optional[str]:
    """
    Convert legacy user_id (hash) to Supabase UUID.
    Returns None if user_id is already a UUID or if mapping fails.
    """
    if not USE_SUPABASE:
        return user_id
    
    # If it's already a UUID format, return as-is
    try:
        uuid.UUID(user_id)
        return user_id
    except ValueError:
        pass
    
    # Try to find user by email if user_id is a hash
    # This is a fallback for migration scenarios
    return None


# =====================================================================
# USER MEMORY (Themes, Personality, Spiritual Journey)
# =====================================================================

def load_user_memory(user_id: str) -> Dict:
    """
    Load a user's memory from Supabase or file.
    Returns a dict compatible with the old file-based format.
    """
    if not USE_SUPABASE:
        return _load_user_memory_file_based(user_id)
    
    try:
        supabase = get_supabase_client(use_service_role=False)
        
        # Get user_memory record
        memory_response = supabase.table("user_memory").select("*").eq("user_id", user_id).execute()
        
        if memory_response.data and len(memory_response.data) > 0:
            memory_data = memory_response.data[0]
            
            # Convert to old format for backward compatibility
            return {
                "user_id": user_id,
                "email": None,  # Will be populated from users table if needed
                "created_at": memory_data.get("updated_at", datetime.now().isoformat()),
                "last_visit": memory_data.get("updated_at", datetime.now().isoformat()),
                "visit_count": 0,  # This is tracked in users table
                "conversations": [],  # Old format - use chats instead
                "themes": memory_data.get("themes", []),
                "journal_entries": [],  # Loaded separately
                "preferences": {
                    "traditions": [],
                    "ui_mode": "standard",
                    "ambient_sound": "Silence"
                },
                "personality_traits": memory_data.get("personality_traits", {}),
                "spiritual_journey": memory_data.get("spiritual_journey", {
                    "primary_concerns": [],
                    "growth_areas": [],
                    "milestones": []
                }),
                "preferred_wisdom_style": memory_data.get("preferred_wisdom_style"),
                "conversation_summary": memory_data.get("conversation_summary", "")
            }
        
        # Return default memory structure
        return _get_default_memory(user_id)
        
    except Exception as e:
        print(f"Error loading user memory from Supabase: {e}")
        return _get_default_memory(user_id)


def save_user_memory(user_id: str, memory: Dict) -> None:
    """Save a user's memory to Supabase or file."""
    if not USE_SUPABASE:
        return _save_user_memory_file_based(user_id, memory)
    
    try:
        supabase = get_supabase_client(use_service_role=False)
        
        # Extract data for user_memory table
        memory_data = {
            "user_id": user_id,
            "themes": memory.get("themes", []),
            "personality_traits": memory.get("personality_traits", {}),
            "spiritual_journey": memory.get("spiritual_journey", {
                "primary_concerns": [],
                "growth_areas": [],
                "milestones": []
            }),
            "preferred_wisdom_style": memory.get("preferred_wisdom_style"),
            "conversation_summary": memory.get("conversation_summary", ""),
            "updated_at": datetime.now().isoformat()
        }
        
        # Upsert user_memory
        supabase.table("user_memory").upsert(memory_data, on_conflict="user_id").execute()
        
    except Exception as e:
        print(f"Error saving user memory to Supabase: {e}")


def _get_default_memory(user_id: str) -> Dict:
    """Return default memory structure."""
    return {
        "user_id": user_id,
        "email": None,
        "created_at": datetime.now().isoformat(),
        "last_visit": datetime.now().isoformat(),
        "visit_count": 0,
        "conversations": [],
        "themes": [],
        "journal_entries": [],
        "preferences": {
            "traditions": [],
            "ui_mode": "standard",
            "ambient_sound": "Silence"
        },
        "personality_traits": {},
        "spiritual_journey": {
            "primary_concerns": [],
            "growth_areas": [],
            "milestones": []
        },
        "preferred_wisdom_style": None,
        "conversation_summary": ""
    }


# =====================================================================
# THEME AND PERSONALITY FUNCTIONS (unchanged logic)
# =====================================================================

def update_themes(memory: Dict, text: str) -> None:
    """Extract and update recurring themes from text."""
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
    
    memory["themes"] = memory["themes"][-15:]


def extract_personality_insights(memory: Dict) -> Dict:
    """Extract personality insights from conversation history."""
    traits = {}
    
    # Get all questions from chats (Supabase) or conversations (file-based)
    all_questions = []
    
    if USE_SUPABASE:
        # Get questions from chat_messages
        user_id = memory.get("user_id")
        if user_id:
            try:
                supabase = get_supabase_client(use_service_role=False)
                # Get all user messages
                chats_response = supabase.table("chats").select("id").eq("user_id", user_id).execute()
                chat_ids = [c["id"] for c in chats_response.data] if chats_response.data else []
                
                if chat_ids:
                    messages_response = supabase.table("chat_messages").select("content").eq("role", "user").in_("chat_id", chat_ids).execute()
                    all_questions = [m["content"].lower() for m in messages_response.data] if messages_response.data else []
            except:
                pass
    else:
        # File-based: get from conversations
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
    
    memory["personality_traits"] = traits
    return traits


def update_spiritual_journey(memory: Dict, question: str, answer: str) -> None:
    """Update spiritual journey tracking based on conversations."""
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
            journey["primary_concerns"] = journey["primary_concerns"][-5:]
    
    # Identify growth areas (themes that appear frequently)
    theme_counts = {}
    
    if USE_SUPABASE:
        # Count themes from chat messages
        user_id = memory.get("user_id")
        if user_id:
            try:
                supabase = get_supabase_client(use_service_role=False)
                chats_response = supabase.table("chats").select("id").eq("user_id", user_id).execute()
                chat_ids = [c["id"] for c in chats_response.data] if chats_response.data else []
                
                if chat_ids:
                    messages_response = supabase.table("chat_messages").select("content").eq("role", "user").in_("chat_id", chat_ids).execute()
                    for msg in messages_response.data or []:
                        content_lower = msg["content"].lower()
                        for theme in themes:
                            if theme in content_lower:
                                theme_counts[theme] = theme_counts.get(theme, 0) + 1
            except:
                pass
    else:
        # File-based: count from conversations
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
    # This would need to be tracked separately in Supabase
    visit_count = memory.get("visit_count", 0)
    if visit_count > 0 and visit_count % 10 == 0:
        milestone = f"Completed {visit_count} conversations"
        if milestone not in journey["milestones"]:
            journey["milestones"].append(milestone)
            journey["milestones"] = journey["milestones"][-10:]


# =====================================================================
# EXCHANGE AND JOURNAL FUNCTIONS
# =====================================================================

def add_exchange(
    memory: Dict, 
    question: str, 
    answer: str, 
    traditions: List[str] = None
) -> Dict:
    """
    Add a Q&A exchange to memory.
    Note: With Supabase, exchanges are stored as chat messages.
    This function maintains backward compatibility.
    """
    # For Supabase, exchanges are handled via chat_messages
    # This function updates themes and spiritual journey
    update_themes(memory, question)
    update_spiritual_journey(memory, question, answer)
    
    # Extract personality insights periodically
    if USE_SUPABASE:
        user_id = memory.get("user_id")
        if user_id:
            try:
                supabase = get_supabase_client(use_service_role=False)
                chats_response = supabase.table("chats").select("id").eq("user_id", user_id).execute()
                total_messages = 0
                if chats_response.data:
                    chat_ids = [c["id"] for c in chats_response.data]
                    messages_response = supabase.table("chat_messages").select("id").in_("chat_id", chat_ids).execute()
                    total_messages = len(messages_response.data) if messages_response.data else 0
                
                if total_messages % 5 == 0:
                    extract_personality_insights(memory)
            except:
                pass
    else:
        # File-based: count from conversations
        exchange_count = sum(len(conv.get("exchanges", [])) for conv in memory.get("conversations", []))
        if exchange_count % 5 == 0:
            extract_personality_insights(memory)
    
    return memory


def add_journal_entry(memory: Dict, entry: str, reflection: str) -> Dict:
    """Add a journal entry to memory (Supabase or file)."""
    user_id = memory.get("user_id")
    
    if USE_SUPABASE and user_id:
        try:
            supabase = get_supabase_client(use_service_role=False)
            supabase.table("journal_entries").insert({
                "user_id": user_id,
                "entry": entry[:1000],
                "reflection": reflection[:500],
                "created_at": datetime.now().isoformat()
            }).execute()
        except Exception as e:
            print(f"Error saving journal entry to Supabase: {e}")
    else:
        # File-based fallback
        memory["journal_entries"].append({
            "date": datetime.now().isoformat(),
            "entry": entry[:1000],
            "reflection": reflection[:500]
        })
        memory["journal_entries"] = memory["journal_entries"][-30:]
    
    return memory


# =====================================================================
# CONTEXT AND SUMMARY FUNCTIONS
# =====================================================================

def get_conversation_summary(memory: Dict, limit: int = 5) -> str:
    """Get a summary of recent conversations for context."""
    if USE_SUPABASE:
        user_id = memory.get("user_id")
        if not user_id:
            return ""
        
        try:
            supabase = get_supabase_client(use_service_role=False)
            # Get recent user messages
            chats_response = supabase.table("chats").select("id").eq("user_id", user_id).order("updated_at", desc=True).limit(5).execute()
            chat_ids = [c["id"] for c in chats_response.data] if chats_response.data else []
            
            if not chat_ids:
                return ""
            
            summaries = []
            for chat_id in chat_ids[:limit]:
                messages_response = supabase.table("chat_messages").select("content, timestamp").eq("chat_id", chat_id).eq("role", "user").order("timestamp", desc=True).limit(1).execute()
                if messages_response.data:
                    msg = messages_response.data[0]
                    date_str = msg["timestamp"][:10] if msg.get("timestamp") else ""
                    summaries.append(f"[{date_str}] Seeker asked about: {msg['content'][:100]}...")
            
            if summaries:
                return "Previous conversations:\n" + "\n".join(summaries)
        except:
            pass
        
        return ""
    else:
        # File-based
        if not memory["conversations"]:
            return ""
        
        summaries = []
        exchange_count = 0
        
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
        return None
    
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
    """Generate context string to include in LLM prompt."""
    parts = []
    
    visit_count = memory.get("visit_count", 0)
    if visit_count > 1:
        parts.append(f"This is a returning seeker (visit #{visit_count}).")
    
    personality = memory.get("personality_traits", {})
    if personality:
        traits_list = [f"{k}: {v}" for k, v in personality.items() if v]
        if traits_list:
            parts.append(f"Personality insights: {', '.join(traits_list)}")
    
    wisdom_style = memory.get("preferred_wisdom_style")
    if wisdom_style:
        parts.append(f"This seeker prefers {wisdom_style} guidance.")
    
    journey = memory.get("spiritual_journey", {})
    if journey.get("primary_concerns"):
        concerns = ", ".join(journey["primary_concerns"][:3])
        parts.append(f"Primary concerns: {concerns}")
    if journey.get("growth_areas"):
        growth = ", ".join(journey["growth_areas"][:3])
        parts.append(f"Areas of growth: {growth}")
    
    themes_summary = get_themes_summary(memory)
    if themes_summary:
        parts.append(themes_summary)
    
    conv_summary = get_conversation_summary(memory, limit=3)
    if conv_summary:
        parts.append(conv_summary)
    
    if memory.get("conversation_summary"):
        parts.append(f"Journey summary: {memory['conversation_summary'][:300]}...")
    
    # Journal themes
    if USE_SUPABASE:
        user_id = memory.get("user_id")
        if user_id:
            try:
                supabase = get_supabase_client(use_service_role=False)
                journal_response = supabase.table("journal_entries").select("entry").eq("user_id", user_id).order("created_at", desc=True).limit(1).execute()
                if journal_response.data:
                    recent_journal = journal_response.data[0]
                    parts.append(f"Recent journal reflection: {recent_journal['entry'][:200]}...")
            except:
                pass
    else:
        if memory.get("journal_entries"):
            recent_journal = memory["journal_entries"][-1]
            parts.append(f"Recent journal reflection: {recent_journal['entry'][:200]}...")
    
    if not parts:
        return ""
    
    return "SEEKER CONTEXT:\n" + "\n".join(parts) + "\n"


# =====================================================================
# CHAT MANAGEMENT (Multiple Conversations like ChatGPT)
# =====================================================================

def generate_chat_title(first_question: str) -> str:
    """
    Generate a short, concise title (2-3 words) from the first question.
    Uses LLM if available, otherwise falls back to smart extraction.
    """
    if not first_question or not first_question.strip():
        return "New Chat"
    
    # Try to generate with LLM first
    if LLM_AVAILABLE:
        try:
            prompt = f"""Create a very short title (2-3 words maximum) that summarizes this question:

"{first_question}"

Return only the title, nothing else. Just 2-3 words that capture the main topic."""
            
            system_prompt = "You are a helpful assistant that creates very short, concise titles (2-3 words) for conversations."
            
            llm_title = generate_with_llm(prompt, system_prompt, max_tokens=20)
            
            # Clean up the response
            llm_title = llm_title.strip()
            # Remove quotes if present
            llm_title = llm_title.strip('"\'')
            # Remove any trailing punctuation
            llm_title = llm_title.rstrip('.,!?;:')
            
            # Count words and validate
            words = llm_title.split()
            if len(words) <= 4 and len(llm_title) > 2 and not llm_title.startswith("Error"):
                # If more than 3 words, take first 3
                if len(words) > 3:
                    llm_title = ' '.join(words[:3])
                return llm_title
        except Exception as e:
            print(f"Error generating title with LLM: {e}")
            # Fall through to fallback
    
    # Fallback: Extract key words from question
    question = first_question.strip()
    question_lower = question.lower()
    
    # Remove common question words and phrases
    prefixes_to_remove = [
        "what is", "what are", "what do", "what does", "what did", "what will",
        "how do", "how does", "how can", "how should", "how did", "how will",
        "why do", "why does", "why did", "why should", "why is", "why are",
        "when do", "when does", "when did", "when will", "when is", "when are",
        "where do", "where does", "where did", "where will", "where is", "where are",
        "who is", "who are", "who do", "who does", "who did", "who will",
        "can you", "could you", "would you", "should i", "can i", "could i",
        "tell me", "explain", "i want", "i need", "i'm", "i am", "i feel", "i think"
    ]
    
    for prefix in prefixes_to_remove:
        if question_lower.startswith(prefix):
            question = question[len(prefix):].strip()
            break
    
    # Remove question mark
    question = question.rstrip('?')
    
    # Extract first 2-3 words
    words = question.split()
    if len(words) > 3:
        words = words[:3]
    
    # Capitalize first letter of each word
    title = ' '.join(word.capitalize() if word else '' for word in words if word)
    
    return title if title else "New Chat"


def create_new_chat(user_id: str, religion: str = None, title: str = None) -> Dict:
    """Create a new chat thread for a user."""
    if not USE_SUPABASE:
        return _create_new_chat_file_based(user_id, religion, title)
    
    try:
        supabase = get_supabase_client(use_service_role=False)
        
        # Generate title if not provided
        if not title:
            # Count existing "New Chat X" titles
            existing_chats = supabase.table("chats").select("title").eq("user_id", user_id).execute()
            existing_numbers = []
            if existing_chats.data:
                for chat in existing_chats.data:
                    chat_title = chat.get("title", "")
                    if chat_title.startswith("New Chat "):
                        try:
                            num = int(chat_title.replace("New Chat ", ""))
                            existing_numbers.append(num)
                        except ValueError:
                            pass
            
            next_num = max(existing_numbers) + 1 if existing_numbers else 1
            title = f"New Chat {next_num}"
        
        # Set all other chats to not current
        supabase.table("chats").update({"is_current": False}).eq("user_id", user_id).execute()
        
        # Create new chat
        chat_data = {
            "user_id": user_id,
            "title": title,
            "religion": religion,
            "is_current": True,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        response = supabase.table("chats").insert(chat_data).execute()
        
        if response.data and len(response.data) > 0:
            chat = response.data[0]
            # Add empty messages array for compatibility
            chat["messages"] = []
            return chat
        
        raise Exception("Failed to create chat")
        
    except Exception as e:
        print(f"Error creating chat in Supabase: {e}")
        # Fallback to file-based
        return _create_new_chat_file_based(user_id, religion, title)


def get_chat(user_id: str, chat_id: str) -> Optional[Dict]:
    """Get a specific chat by ID."""
    if not USE_SUPABASE:
        return _get_chat_file_based(user_id, chat_id)
    
    try:
        supabase = get_supabase_client(use_service_role=False)
        response = supabase.table("chats").select("*").eq("id", chat_id).eq("user_id", user_id).execute()
        
        if response.data and len(response.data) > 0:
            chat = response.data[0]
            # Load messages
            messages_response = supabase.table("chat_messages").select("*").eq("chat_id", chat_id).order("timestamp").execute()
            chat["messages"] = [
                {
                    "role": m["role"],
                    "content": m["content"],
                    "timestamp": m["timestamp"]
                }
                for m in (messages_response.data or [])
            ]
            return chat
        
        return None
    except Exception as e:
        print(f"Error getting chat from Supabase: {e}")
        return _get_chat_file_based(user_id, chat_id)


def get_all_chats(user_id: str) -> List[Dict]:
    """Get all chats for a user (summary only, not full messages)."""
    if not USE_SUPABASE:
        return _get_all_chats_file_based(user_id)
    
    try:
        supabase = get_supabase_client(use_service_role=False)
        chats_response = supabase.table("chats").select("id, title, created_at, updated_at, religion").eq("user_id", user_id).order("updated_at", desc=True).execute()
        
        summaries = []
        if chats_response.data:
            for chat in chats_response.data:
                # Get message count and preview
                messages_response = supabase.table("chat_messages").select("content").eq("chat_id", chat["id"]).order("timestamp", desc=True).limit(1).execute()
                
                message_count_response = supabase.table("chat_messages").select("id", count="exact").eq("chat_id", chat["id"]).execute()
                message_count = message_count_response.count if hasattr(message_count_response, 'count') else 0
                
                preview = ""
                if messages_response.data:
                    preview = messages_response.data[0]["content"][:50] + "..."
                
                summaries.append({
                    "id": chat["id"],
                    "title": chat.get("title", "Untitled"),
                    "created_at": chat.get("created_at"),
                    "updated_at": chat.get("updated_at"),
                    "religion": chat.get("religion"),
                    "message_count": message_count,
                    "preview": preview
                })
        
        return summaries
    except Exception as e:
        print(f"Error getting chats from Supabase: {e}")
        return _get_all_chats_file_based(user_id)


def get_current_chat_id(user_id: str) -> Optional[str]:
    """Get the ID of the user's current active chat."""
    if not USE_SUPABASE:
        memory = load_user_memory(user_id)
        return memory.get("current_chat_id")
    
    try:
        supabase = get_supabase_client(use_service_role=False)
        response = supabase.table("chats").select("id").eq("user_id", user_id).eq("is_current", True).limit(1).execute()
        
        if response.data and len(response.data) > 0:
            return response.data[0]["id"]
        return None
    except Exception as e:
        print(f"Error getting current chat from Supabase: {e}")
        memory = load_user_memory(user_id)
        return memory.get("current_chat_id")


def set_current_chat(user_id: str, chat_id: str) -> bool:
    """Set the current active chat."""
    if not USE_SUPABASE:
        return _set_current_chat_file_based(user_id, chat_id)
    
    try:
        supabase = get_supabase_client(use_service_role=False)
        
        # Verify chat exists and belongs to user
        chat_response = supabase.table("chats").select("id").eq("id", chat_id).eq("user_id", user_id).execute()
        if not chat_response.data:
            return False
        
        # Set all chats to not current
        supabase.table("chats").update({"is_current": False}).eq("user_id", user_id).execute()
        
        # Set this chat as current
        supabase.table("chats").update({"is_current": True}).eq("id", chat_id).execute()
        
        return True
    except Exception as e:
        print(f"Error setting current chat in Supabase: {e}")
        return _set_current_chat_file_based(user_id, chat_id)


def add_message_to_chat(
    user_id: str, 
    chat_id: str, 
    role: str, 
    content: str,
    traditions: List[str] = None,
    sources: List[Dict] = None
) -> Optional[Dict]:
    """Add a message to a specific chat."""
    if not USE_SUPABASE:
        return _add_message_to_chat_file_based(user_id, chat_id, role, content)
    
    try:
        supabase = get_supabase_client(use_service_role=False)
        
        # Verify chat belongs to user
        chat_response = supabase.table("chats").select("id, title").eq("id", chat_id).eq("user_id", user_id).execute()
        if not chat_response.data:
            return None
        
        chat = chat_response.data[0]
        
        # Add message
        message_data = {
            "chat_id": chat_id,
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "traditions": traditions or [],
            "sources": sources or []
        }
        
        supabase.table("chat_messages").insert(message_data).execute()
        
        # Auto-generate title from first user message
        if chat.get("title", "").startswith("New Chat") and role == "user":
            new_title = generate_chat_title(content)
            supabase.table("chats").update({"title": new_title}).eq("id", chat_id).execute()
            chat["title"] = new_title
        
        # Update themes if user message
        if role == "user":
            memory = load_user_memory(user_id)
            update_themes(memory, content)
            save_user_memory(user_id, memory)
        
        # Return updated chat
        return get_chat(user_id, chat_id)
        
    except Exception as e:
        print(f"Error adding message to chat in Supabase: {e}")
        return _add_message_to_chat_file_based(user_id, chat_id, role, content)


def get_chat_messages(user_id: str, chat_id: str) -> List[Dict]:
    """Get all messages from a specific chat."""
    chat = get_chat(user_id, chat_id)
    if not chat:
        return []
    return chat.get("messages", [])


def delete_chat(user_id: str, chat_id: str) -> bool:
    """Delete a chat thread."""
    if not USE_SUPABASE:
        return _delete_chat_file_based(user_id, chat_id)
    
    try:
        supabase = get_supabase_client(use_service_role=False)
        
        # Verify chat belongs to user
        chat_response = supabase.table("chats").select("id, is_current").eq("id", chat_id).eq("user_id", user_id).execute()
        if not chat_response.data:
            return False
        
        was_current = chat_response.data[0].get("is_current", False)
        
        # Delete chat (messages will be cascade deleted)
        supabase.table("chats").delete().eq("id", chat_id).execute()
        
        # If deleted chat was current, set another as current
        if was_current:
            other_chat = supabase.table("chats").select("id").eq("user_id", user_id).order("updated_at", desc=True).limit(1).execute()
            if other_chat.data:
                supabase.table("chats").update({"is_current": True}).eq("id", other_chat.data[0]["id"]).execute()
        
        return True
    except Exception as e:
        print(f"Error deleting chat from Supabase: {e}")
        return _delete_chat_file_based(user_id, chat_id)


def rename_chat(user_id: str, chat_id: str, new_title: str) -> bool:
    """Rename a chat thread."""
    if not USE_SUPABASE:
        return _rename_chat_file_based(user_id, chat_id, new_title)
    
    try:
        supabase = get_supabase_client(use_service_role=False)
        response = supabase.table("chats").update({"title": new_title[:100]}).eq("id", chat_id).eq("user_id", user_id).execute()
        return response.data is not None and len(response.data) > 0
    except Exception as e:
        print(f"Error renaming chat in Supabase: {e}")
        return _rename_chat_file_based(user_id, chat_id, new_title)


def get_or_create_current_chat(user_id: str, religion: str = None) -> Dict:
    """Get the current chat, or create one if none exists."""
    current_id = get_current_chat_id(user_id)
    if current_id:
        chat = get_chat(user_id, current_id)
        if chat:
            return chat
    
    # Check if any chats exist
    all_chats = get_all_chats(user_id)
    if all_chats:
        # Set first chat as current
        set_current_chat(user_id, all_chats[0]["id"])
        return get_chat(user_id, all_chats[0]["id"])
    
    # Create new chat
    return create_new_chat(user_id, religion)


def migrate_old_conversations_to_chats(user_id: str) -> int:
    """Migrate old-style conversations to new chat format."""
    # This function is mainly for file-based migration
    # With Supabase, we start fresh with chats
    if USE_SUPABASE:
        return 0
    
    return _migrate_old_conversations_to_chats_file_based(user_id)


def migrate_session_memory_to_account(session_id: str, email: str) -> bool:
    """Migrate session-based memory to account-based memory."""
    # With Supabase, this is handled via user_id mapping
    # The migration script will handle this
    return True


# =====================================================================
# FILE-BASED FALLBACK FUNCTIONS
# =====================================================================

def _load_user_memory_file_based(user_id: str) -> Dict:
    """Fallback file-based memory loading."""
    def get_user_file(user_id: str) -> str:
        os.makedirs(USER_DATA_DIR, exist_ok=True)
        return os.path.join(USER_DATA_DIR, f"{user_id}.json")
    
    filepath = get_user_file(user_id)
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    
    return _get_default_memory(user_id)


def _save_user_memory_file_based(user_id: str, memory: Dict) -> None:
    """Fallback file-based memory saving."""
    def get_user_file(user_id: str) -> str:
        os.makedirs(USER_DATA_DIR, exist_ok=True)
        return os.path.join(USER_DATA_DIR, f"{user_id}.json")
    
    filepath = get_user_file(user_id)
    memory["last_visit"] = datetime.now().isoformat()
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(memory, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving memory: {e}")


def _create_new_chat_file_based(user_id: str, religion: str = None, title: str = None) -> Dict:
    """Fallback file-based chat creation."""
    memory = _load_user_memory_file_based(user_id)
    
    if "chats" not in memory:
        memory["chats"] = []
    
    if not title:
        existing_numbers = []
        for chat in memory["chats"]:
            chat_title = chat.get("title", "")
            if chat_title.startswith("New Chat "):
                try:
                    num = int(chat_title.replace("New Chat ", ""))
                    existing_numbers.append(num)
                except ValueError:
                    pass
        
        next_num = max(existing_numbers) + 1 if existing_numbers else 1
        title = f"New Chat {next_num}"
    
    chat_id = str(uuid.uuid4())[:8]
    new_chat = {
        "id": chat_id,
        "title": title,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "religion": religion,
        "messages": []
    }
    
    memory["chats"].insert(0, new_chat)
    memory["current_chat_id"] = chat_id
    memory["chats"] = memory["chats"][:50]
    
    _save_user_memory_file_based(user_id, memory)
    return new_chat


def _get_chat_file_based(user_id: str, chat_id: str) -> Optional[Dict]:
    """Fallback file-based chat retrieval."""
    memory = _load_user_memory_file_based(user_id)
    for chat in memory.get("chats", []):
        if chat["id"] == chat_id:
            return chat
    return None


def _get_all_chats_file_based(user_id: str) -> List[Dict]:
    """Fallback file-based chat list."""
    memory = _load_user_memory_file_based(user_id)
    chats = memory.get("chats", [])
    
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


def _set_current_chat_file_based(user_id: str, chat_id: str) -> bool:
    """Fallback file-based current chat setting."""
    memory = _load_user_memory_file_based(user_id)
    
    chat_exists = any(c["id"] == chat_id for c in memory.get("chats", []))
    if not chat_exists:
        return False
    
    memory["current_chat_id"] = chat_id
    _save_user_memory_file_based(user_id, memory)
    return True


def _add_message_to_chat_file_based(user_id: str, chat_id: str, role: str, content: str) -> Optional[Dict]:
    """Fallback file-based message addition."""
    memory = _load_user_memory_file_based(user_id)
    
    for chat in memory.get("chats", []):
        if chat["id"] == chat_id:
            chat["messages"].append({
                "role": role,
                "content": content,
                "timestamp": datetime.now().isoformat()
            })
            chat["updated_at"] = datetime.now().isoformat()
            
            if chat["title"] == "New Conversation" or chat["title"].startswith("New Chat"):
                chat["title"] = generate_chat_title(content)
            
            memory["chats"].remove(chat)
            memory["chats"].insert(0, chat)
            
            _save_user_memory_file_based(user_id, memory)
            
            if role == "user":
                update_themes(memory, content)
                _save_user_memory_file_based(user_id, memory)
            
            return chat
    
    return None


def _delete_chat_file_based(user_id: str, chat_id: str) -> bool:
    """Fallback file-based chat deletion."""
    memory = _load_user_memory_file_based(user_id)
    
    original_count = len(memory.get("chats", []))
    memory["chats"] = [c for c in memory.get("chats", []) if c["id"] != chat_id]
    
    if len(memory["chats"]) < original_count:
        if memory.get("current_chat_id") == chat_id:
            if memory["chats"]:
                memory["current_chat_id"] = memory["chats"][0]["id"]
            else:
                memory["current_chat_id"] = None
        
        _save_user_memory_file_based(user_id, memory)
        return True
    
    return False


def _rename_chat_file_based(user_id: str, chat_id: str, new_title: str) -> bool:
    """Fallback file-based chat renaming."""
    memory = _load_user_memory_file_based(user_id)
    
    for chat in memory.get("chats", []):
        if chat["id"] == chat_id:
            chat["title"] = new_title[:100]
            _save_user_memory_file_based(user_id, memory)
            return True
    
    return False


def _migrate_old_conversations_to_chats_file_based(user_id: str) -> int:
    """Fallback file-based conversation migration."""
    memory = _load_user_memory_file_based(user_id)
    
    old_convs = memory.get("conversations", [])
    if not old_convs:
        return 0
    
    if "chats" not in memory:
        memory["chats"] = []
    
    migrated = 0
    
    for conv in old_convs:
        exchanges = conv.get("exchanges", [])
        if not exchanges:
            continue
        
        chat_id = str(uuid.uuid4())[:8]
        
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
    
    memory["chats"].sort(key=lambda x: x.get("updated_at", ""), reverse=True)
    
    if memory["chats"] and not memory.get("current_chat_id"):
        memory["current_chat_id"] = memory["chats"][0]["id"]
    
    _save_user_memory_file_based(user_id, memory)
    return migrated

