"""
Q&A and Advisor Module for Divine Wisdom Guide

Handles all interactions with the LLM, including:
- Standard spiritual guidance (single LLM)
- Multi-agent spiritual guidance (4 specialized agents)
- Comparative theology
- Guided meditations
- Journal reflections
- Daily wisdom generation

Supports both:
- Google Gemini API (for cloud deployment)
- Ollama (for local development)
"""

from typing import List, Optional, Tuple, Dict
import random

from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.messages import SystemMessage, HumanMessage

from config import (
    VECTORSTORE_DIR, 
    EMBEDDING_MODEL_NAME, 
    OLLAMA_MODEL,
    TRADITIONS,
    ADVISOR_NAME,
    ENABLE_CRISIS_DETECTION,
    LLM_PROVIDER,
    GEMINI_API_KEY,
    GEMINI_MODEL
)
from safety import (
    detect_crisis, 
    get_crisis_response, 
    detect_deity_treatment,
    get_deity_clarification,
    get_theological_humility_reminder,
    should_add_humility_reminder
)
from memory import get_context_for_llm

# Import LLM providers based on configuration
if LLM_PROVIDER == "gemini":
    import google.generativeai as genai
    # Configure Gemini
    if GEMINI_API_KEY:
        genai.configure(api_key=GEMINI_API_KEY)
        _gemini_model = genai.GenerativeModel(GEMINI_MODEL)
    else:
        print("WARNING: GEMINI_API_KEY not set. LLM calls will fail.")
        _gemini_model = None
else:
    from langchain_community.llms import Ollama
    _gemini_model = None

# Import multi-agent system
try:
    from agents import multi_agent_guidance, compare_religions_on_topic
    MULTI_AGENT_AVAILABLE = True
except ImportError:
    MULTI_AGENT_AVAILABLE = False

# Cache vectorstore and embeddings to avoid reloading
_vectorstore_cache = None
_embeddings_cache = None


def get_optimized_llm(max_tokens: int = 512):
    """
    Get an LLM instance based on the configured provider.
    
    Args:
        max_tokens: Maximum tokens to generate (default 512 for speed)
    
    Returns:
        For Gemini: Returns None (we use the global _gemini_model directly)
        For Ollama: Returns an Ollama instance
    """
    if LLM_PROVIDER == "gemini":
        # For Gemini, we use the direct API, not LangChain wrapper
        return None
    else:
        # Ollama for local development
        return Ollama(
            model=OLLAMA_MODEL,
            temperature=0.7,
            num_predict=max_tokens,
            top_p=0.9,
            repeat_penalty=1.1,
        )


def generate_with_llm(prompt: str, system_prompt: str = None, max_tokens: int = 2048) -> str:
    """
    Generate text using the configured LLM provider.
    
    Args:
        prompt: The user prompt/question
        system_prompt: Optional system instructions
        max_tokens: Maximum tokens to generate
    
    Returns:
        Generated text response
    """
    if LLM_PROVIDER == "gemini":
        if not _gemini_model:
            return "Error: Gemini API key not configured."
        
        try:
            # Combine system prompt and user prompt for Gemini
            full_prompt = prompt
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n{prompt}"
            
            # Safety settings - allow religious/spiritual content
            safety_settings = {
                genai.types.HarmCategory.HARM_CATEGORY_HARASSMENT: genai.types.HarmBlockThreshold.BLOCK_NONE,
                genai.types.HarmCategory.HARM_CATEGORY_HATE_SPEECH: genai.types.HarmBlockThreshold.BLOCK_NONE,
                genai.types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: genai.types.HarmBlockThreshold.BLOCK_NONE,
                genai.types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: genai.types.HarmBlockThreshold.BLOCK_NONE,
            }
            
            # Generate with Gemini
            response = _gemini_model.generate_content(
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=max_tokens,
                    temperature=0.7,
                    top_p=0.9,
                ),
                safety_settings=safety_settings
            )
            
            # Extract text from response - handle all cases
            # Check if we have valid candidates with content
            if hasattr(response, 'candidates') and response.candidates:
                candidate = response.candidates[0]
                finish_reason = candidate.finish_reason if hasattr(candidate, 'finish_reason') else 'N/A'
                # 1=STOP (good), 2=MAX_TOKENS (truncated), 3=SAFETY, 4=RECITATION, 5=OTHER
                print(f"[DEBUG] Candidate finish_reason: {finish_reason} (1=OK, 2=TRUNCATED, 3=SAFETY)")
                
                if hasattr(candidate, 'content') and candidate.content:
                    if hasattr(candidate.content, 'parts') and candidate.content.parts:
                        # Combine all parts (sometimes response is split across multiple parts)
                        full_text = ""
                        for part in candidate.content.parts:
                            if hasattr(part, 'text'):
                                full_text += part.text
                        print(f"[DEBUG] Extracted text length: {len(full_text)} chars, ~{len(full_text.split())} words")
                        return full_text
            
            # If no valid content, return fallback
            print("[DEBUG] No valid content in response, using fallback")
            return "I sense your question touches on deep spiritual matters. The wisdom traditions teach us to approach life with patience and compassion. Please share more about what guidance you seek."
                
        except Exception as e:
            print(f"Gemini API error: {e}")
            return "I'm here to offer spiritual guidance. Could you please rephrase your question?"
    else:
        # Ollama
        llm = get_optimized_llm(max_tokens)
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"
        return llm.invoke(full_prompt)


def get_vectorstore():
    """Get or create cached vectorstore instance."""
    global _vectorstore_cache, _embeddings_cache
    
    if _vectorstore_cache is None:
        if _embeddings_cache is None:
            _embeddings_cache = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)
        _vectorstore_cache = Chroma(
        persist_directory=VECTORSTORE_DIR,
            embedding_function=_embeddings_cache,
        )
    
    return _vectorstore_cache


def retrieve(question: str, traditions: Optional[List[str]] = None, k: int = 6):
    """
    Retrieve relevant passages from scriptures.
    Reduced default k from 8 to 6 for faster processing.
    """
    db = get_vectorstore()

    if traditions and len(traditions) > 0 and "All Traditions" not in traditions:
        if len(traditions) == 1:
            return db.similarity_search(
                question, k=k, 
                filter={"tradition": traditions[0]}
            )
        else:
            return db.similarity_search(
                question, k=k,
                filter={"tradition": {"$in": traditions}}
            )

    return db.similarity_search(question, k=k)


def retrieve_comparative(question: str, traditions: List[str], k_per_tradition: int = 3):
    """
    Retrieve passages from multiple traditions for comparison.
    Returns a dict mapping tradition -> documents.
    """
    db = get_vectorstore()
    results = {}
    
    for tradition in traditions:
        try:
            docs = db.similarity_search(
                question, 
                k=k_per_tradition,
                filter={"tradition": tradition}
            )
            if docs:
                results[tradition] = docs
        except Exception:
            continue
    
    return results


def context_to_text(docs, max_chars_per_doc: int = 400):
    """
    Format retrieved documents into context for the LLM.
    Truncate long documents to speed up processing.
    """
    blocks = []
    for i, d in enumerate(docs, 1):
        tradition = d.metadata.get('tradition', 'Unknown')
        scripture = d.metadata.get('scripture_name', d.metadata.get('book_title', 'Unknown'))
        content = d.page_content.strip()
        # Truncate content if too long
        if len(content) > max_chars_per_doc:
            content = content[:max_chars_per_doc] + "..."
        blocks.append(
            f"[{i}] {tradition} - {scripture}\n"
            f"{content}"
        )
    return "\n\n".join(blocks)


def get_advisor_system_prompt(traditions_used: List[str], mode: str = "standard") -> str:
    """Generate system prompt based on mode."""
    traditions_str = ", ".join(traditions_used) if traditions_used else "multiple spiritual traditions"
    
    base_prompt = f"""You are {ADVISOR_NAME}, a compassionate and wise spiritual counselor who draws upon 
the sacred wisdom of {traditions_str} to guide seekers on their life journey.

YOUR ROLE:
- You are NOT just a knowledge base. You are a caring advisor who helps people with real-life challenges.
- People come to you with questions about their lives: relationships, career, purpose, suffering, 
  moral dilemmas, grief, hope, and the search for meaning.
- You listen deeply, offer comfort, and provide guidance rooted in timeless spiritual wisdom.

YOUR VOICE:
- Speak with warmth, wisdom, and gentle authority
- Use metaphors and stories when they help illuminate truth
- Be respectful of all traditions - find common threads of wisdom
- Never be preachy or judgmental
- Acknowledge when questions touch on mystery beyond human understanding
- Balance the transcendent with the practical

IMPORTANT: You are a guide pointing toward ancient wisdom, not a deity. Be humble about your nature as an AI."""

    if mode == "prayer":
        base_prompt += """

PRAYER MODE: The seeker has entered a contemplative space. Keep your responses brief, 
gentle, and poetic. Focus on comfort and presence rather than detailed analysis. 
Speak as one might in a quiet sanctuary."""

    elif mode == "journal":
        base_prompt += """

JOURNAL MODE: The seeker is sharing personal reflections. Your role is to:
- Mirror back what you hear in their words
- Notice themes and patterns gently
- Suggest relevant wisdom without overwhelming
- Encourage continued reflection
- Be a compassionate witness, not a problem-solver"""

    elif mode == "meditation":
        base_prompt += """

MEDITATION MODE: Generate calming, guided meditation scripts. Include:
- A centering breath exercise
- Visualization based on the seeker's needs
- References to relevant spiritual wisdom
- A gentle return to awareness
- Keep the tone slow, spacious, and peaceful"""

    return base_prompt


def ask_question(
    question: str, 
    traditions: Optional[List[str]] = None,
    conversation_history: Optional[List[Tuple[str, str]]] = None,
    user_memory: Optional[Dict] = None,
    mode: str = "standard",
    message_count: int = 0
) -> Tuple[str, List, bool]:
    """
    Process a user's question and return spiritual guidance.
    
    Returns:
        Tuple of (response text, retrieved documents, is_crisis)
    """
    # Crisis detection first
    if ENABLE_CRISIS_DETECTION:
        is_crisis, crisis_type = detect_crisis(question)
        if is_crisis:
            crisis_response = get_crisis_response(crisis_type)
            return crisis_response, [], True
    
    # Check for deity treatment
    if detect_deity_treatment(question):
        clarification = get_deity_clarification()
        # Continue with response but prepend clarification
    else:
        clarification = ""
    
    # Retrieve relevant passages
    docs = retrieve(question, traditions)
    context = context_to_text(docs)
    
    # Debug: show what we retrieved
    print(f"[DEBUG] Retrieved {len(docs)} scripture passages")
    print(f"[DEBUG] Context length: {len(context)} chars")

    # Get traditions in context
    traditions_in_context = list(set(
        d.metadata.get('tradition', 'Unknown') for d in docs
    ))
    print(f"[DEBUG] Traditions found: {traditions_in_context}")
    
    system_prompt = get_advisor_system_prompt(traditions_in_context, mode)
    
    # Build memory context
    memory_context = ""
    if user_memory:
        memory_context = get_context_for_llm(user_memory)
    
    # Build conversation context (reduced from 3 to 2 for faster processing)
    history_text = ""
    if conversation_history and len(conversation_history) > 0:
        recent_history = conversation_history[-2:]  # Reduced from 3 to 2
        history_parts = []
        for user_q, advisor_a in recent_history:
            # Truncate both question and answer for faster processing
            user_q_truncated = user_q[:150] + "..." if len(user_q) > 150 else user_q
            advisor_a_truncated = advisor_a[:200] + "..." if len(advisor_a) > 200 else advisor_a
            history_parts.append(f"Seeker: {user_q_truncated}\nAdvisor: {advisor_a_truncated}")
        history_text = "\n\n".join(history_parts)
    
    # Mode-specific prompts
    if mode == "journal":
        user_prompt = f"""SACRED WISDOM (for reference):
{context}

{memory_context}

SEEKER'S JOURNAL ENTRY:
{question}

Reflect back what you notice in their words. Highlight themes gently. 
Suggest one piece of wisdom that resonates with their reflection.
Keep your response warm and supportive."""

    elif mode == "meditation":
        user_prompt = f"""SACRED WISDOM (for inspiration):
{context}

{memory_context}

SEEKER'S NEED:
{question}

Create a 3-5 minute guided meditation script that:
1. Begins with centering breaths
2. Uses imagery and wisdom from the passages above
3. Addresses their specific need
4. Ends with gentle return to awareness

Write in second person ("You are..."), with [PAUSE] markers for silence."""

    else:  # standard or prayer
        user_prompt = f"""SACRED WISDOM (from scriptures):
{context}

{memory_context}

{f"PREVIOUS CONVERSATION:{chr(10)}{history_text}" if history_text else ""}

SEEKER'S QUESTION:
{question}

Provide guidance that:
- Addresses their specific situation with empathy
- Draws relevant wisdom from the scripture passages above
- Offers practical direction they can apply to their life
- Leaves them with hope and clarity

{"Keep your response brief and poetic." if mode == "prayer" else ""}

Your guidance:"""

    # Generate response using configured LLM (Gemini or Ollama)
    # Increase tokens for fuller responses with scripture citations
    response = generate_with_llm(user_prompt, system_prompt, max_tokens=2048)
    
    # Debug: print response length
    print(f"[DEBUG] Response length: {len(response)} chars")
    
    # Add clarifications if needed
    if clarification:
        response = clarification + "\n\n---\n\n" + response
    
    # Add humility reminder periodically
    if should_add_humility_reminder(message_count):
        response += "\n\n---\n" + get_theological_humility_reminder()
    
    return response, docs, False


def ask_question_multi_agent(
    question: str, 
    traditions: Optional[List[str]] = None,
    conversation_history: Optional[List[Tuple[str, str]]] = None,
    user_memory: Optional[Dict] = None,
    message_count: int = 0
) -> Tuple[str, List, bool, Optional[Dict]]:
    """
    Process a user's question using the MULTI-AGENT system.
    
    Uses 4 specialized agents:
    - Compassion Agent: Emotional grounding
    - Scripture Agent: Accurate citations
    - Scholar Agent: Theological interpretation
    - Guidance Agent: Practical advice
    
    Returns:
        Tuple of (response text, retrieved documents, is_crisis, agent_outputs)
    """
    if not MULTI_AGENT_AVAILABLE:
        # Fall back to regular single-agent
        response, docs, is_crisis = ask_question(
            question, traditions, conversation_history, user_memory, "standard", message_count
        )
        return response, docs, is_crisis, None
    
    # Crisis detection first
    if ENABLE_CRISIS_DETECTION:
        is_crisis, crisis_type = detect_crisis(question)
        if is_crisis:
            crisis_response = get_crisis_response(crisis_type)
            return crisis_response, [], True, None
    
    # Check for deity treatment
    clarification = ""
    if detect_deity_treatment(question):
        clarification = get_deity_clarification()
    
    # Retrieve relevant passages
    docs = retrieve(question, traditions)
    context = context_to_text(docs)

    # Build user context from memory
    user_context = ""
    if user_memory:
        user_context = get_context_for_llm(user_memory)
    
    # Run multi-agent system
    response, agent_outputs = multi_agent_guidance(
        question=question,
        scripture_context=context,
        traditions=traditions,
        user_context=user_context
    )
    
    # Add clarifications if needed
    if clarification:
        response = clarification + "\n\n---\n\n" + response
    
    # Add humility reminder periodically
    if should_add_humility_reminder(message_count):
        response += "\n\n---\n" + get_theological_humility_reminder()
    
    return response, docs, False, agent_outputs


def compare_traditions(
    topic: str,
    traditions: List[str] = None
) -> Tuple[str, Dict]:
    """
    Generate a comparative view of how different traditions address a topic.
    """
    if not traditions or len(traditions) < 2:
        # Default to major traditions
        traditions = ["Christianity", "Buddhism", "Hinduism", "Islam", "Taoism"]
    
    # Retrieve from each tradition
    comparative_docs = retrieve_comparative(topic, traditions)
    
    if not comparative_docs:
        return "I couldn't find relevant passages on this topic across traditions.", {}
    
    # Format context for comparison
    context_parts = []
    for tradition, docs in comparative_docs.items():
        icon = TRADITIONS.get(tradition, {}).get('icon', '📖')
        context_parts.append(f"\n{icon} **{tradition}**:")
        for doc in docs:
            scripture = doc.metadata.get('scripture_name', 'Unknown')
            context_parts.append(f"[{scripture}]: {doc.page_content.strip()[:400]}...")
    
    context = "\n".join(context_parts)
    
    system_prompt = f"""You are {ADVISOR_NAME}, offering comparative spiritual wisdom.
Your role is to show how different traditions approach the same fundamental human questions,
highlighting both unique perspectives and universal truths."""

    user_prompt = f"""TOPIC: {topic}

PASSAGES FROM DIFFERENT TRADITIONS:
{context}

Please provide a thoughtful comparison that:
1. Briefly summarizes each tradition's perspective
2. Highlights unique insights from each
3. Identifies common threads and universal wisdom
4. Offers a synthesis that honors all perspectives

Format with clear sections for each tradition, then a "Common Wisdom" section."""

    response = generate_with_llm(user_prompt, system_prompt, max_tokens=1500)
    
    return response, comparative_docs


def generate_daily_wisdom(
    user_themes: List[str] = None,
    traditions: List[str] = None
) -> Tuple[str, str, str]:
    """
    Generate a personalized daily wisdom/devotional.
    
    Returns:
        Tuple of (wisdom_text, source_tradition, source_scripture)
    """
    # Build a query based on themes or use generic
    if user_themes and len(user_themes) > 0:
        theme = random.choice(user_themes)
        query = f"wisdom guidance inspiration {theme}"
    else:
        themes = ["hope", "peace", "strength", "wisdom", "love", "patience", "gratitude", "courage"]
        query = f"wisdom guidance {random.choice(themes)}"
    
    # Retrieve a passage
    docs = retrieve(query, traditions, k=3)
    
    if not docs:
        return (
            "May this day bring you moments of peace and clarity on your journey.",
            "Universal Wisdom",
            ""
        )
    
    # Pick one randomly for variety
    doc = random.choice(docs)
    tradition = doc.metadata.get('tradition', 'Unknown')
    scripture = doc.metadata.get('scripture_name', 'Unknown')
    passage = doc.page_content.strip()[:500]
    
    # Generate a reflection on it
    system_prompt = f"""You are {ADVISOR_NAME}. Create a brief, inspiring daily reflection."""
    
    user_prompt = f"""Based on this passage from {tradition}:

"{passage}"

Write a 2-3 sentence daily wisdom reflection that:
- Captures the essence of this teaching
- Makes it relevant to modern daily life
- Inspires and uplifts

Keep it concise and memorable."""

    response = generate_with_llm(user_prompt, system_prompt, max_tokens=256)

    return response, tradition, scripture


def generate_journal_reflection(entry: str, user_memory: Dict = None) -> str:
    """
    Generate a gentle reflection on a journal entry.
    """
    # Get some wisdom for context
    docs = retrieve(entry, k=3)
    context = context_to_text(docs) if docs else ""
    
    memory_context = get_context_for_llm(user_memory) if user_memory else ""
    
    system_prompt = f"""You are {ADVISOR_NAME} in journal reflection mode.
You are not solving problems - you are being a compassionate witness.
Mirror back what you hear, notice patterns gently, and offer one small piece of wisdom."""

    user_prompt = f"""RELEVANT WISDOM:
{context}

{memory_context}

JOURNAL ENTRY:
{entry}

Offer a gentle reflection that:
1. Acknowledges what you hear in their words
2. Notices any themes or patterns (especially from past entries)
3. Shares one relevant piece of wisdom for contemplation
4. Ends with an open question for further reflection

Keep your tone warm, curious, and supportive."""

    response = generate_with_llm(user_prompt, system_prompt, max_tokens=1500)

    return response


def get_available_traditions() -> List[str]:
    """Return list of traditions that have scriptures in the vectorstore."""
    db = get_vectorstore()
    try:
        docs = db.similarity_search("wisdom guidance life", k=50)
        traditions = set()
        for d in docs:
            if 'tradition' in d.metadata:
                traditions.add(d.metadata['tradition'])
            elif 'book_title' in d.metadata:
                traditions.add(d.metadata['book_title'])
        return sorted(list(traditions))
    except Exception:
        return list(TRADITIONS.keys())
