from typing import List, Optional, Tuple

from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.llms import Ollama
from langchain_core.messages import SystemMessage, HumanMessage

from config import (
    VECTORSTORE_DIR, 
    EMBEDDING_MODEL_NAME, 
    OLLAMA_MODEL,
    TRADITIONS,
    ADVISOR_NAME
)


def get_vectorstore():
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)
    return Chroma(
        persist_directory=VECTORSTORE_DIR,
        embedding_function=embeddings,
    )


def retrieve(question: str, traditions: Optional[List[str]] = None, k: int = 8):
    """
    Retrieve relevant passages from scriptures.
    Can filter by specific religious traditions.
    """
    db = get_vectorstore()
    
    if traditions and len(traditions) > 0 and "All Traditions" not in traditions:
        # Build filter for multiple traditions
        if len(traditions) == 1:
            return db.similarity_search(
                question, k=k, 
                filter={"tradition": traditions[0]}
            )
        else:
            # ChromaDB uses $in for multiple values
            return db.similarity_search(
                question, k=k,
                filter={"tradition": {"$in": traditions}}
            )
    
    return db.similarity_search(question, k=k)


def context_to_text(docs):
    """Format retrieved documents into context for the LLM."""
    blocks = []
    for i, d in enumerate(docs, 1):
        tradition = d.metadata.get('tradition', 'Unknown')
        scripture = d.metadata.get('scripture_name', d.metadata.get('book_title', 'Unknown'))
        blocks.append(
            f"[{i}] {tradition} - {scripture}\n"
            f"{d.page_content.strip()}"
        )
    return "\n\n".join(blocks)


def get_advisor_system_prompt(traditions_used: List[str]) -> str:
    """
    Generate a system prompt that makes the AI act as a wise spiritual advisor.
    """
    traditions_str = ", ".join(traditions_used) if traditions_used else "multiple spiritual traditions"
    
    return f"""You are {ADVISOR_NAME}, a compassionate and wise spiritual counselor who draws upon 
the sacred wisdom of {traditions_str} to guide seekers on their life journey.

YOUR ROLE:
- You are NOT just a knowledge base. You are a caring advisor who helps people with real-life challenges.
- People come to you with questions about their lives: relationships, career, purpose, suffering, 
  moral dilemmas, grief, hope, and the search for meaning.
- You listen deeply, offer comfort, and provide guidance rooted in timeless spiritual wisdom.

YOUR APPROACH:
1. ACKNOWLEDGE their feelings and situation with empathy
2. REFLECT on what the sacred texts teach about their situation  
3. OFFER practical wisdom and actionable guidance
4. INSPIRE hope and encourage their spiritual growth
5. When appropriate, share relevant passages or teachings that illuminate their path

YOUR VOICE:
- Speak with warmth, wisdom, and gentle authority
- Use metaphors and stories when they help illuminate truth
- Be respectful of all traditions - find common threads of wisdom
- Never be preachy or judgmental
- Acknowledge when questions touch on mystery beyond human understanding
- Balance the transcendent with the practical

IMPORTANT GUIDELINES:
- Draw wisdom from the provided scripture passages, but apply it to their personal situation
- If asked about something the scriptures don't address, offer wisdom based on the principles and values 
  the traditions teach
- Recognize that seekers may be going through difficult times - be sensitive and supportive
- When traditions offer different perspectives, present them thoughtfully
- Always leave the seeker with hope and a sense of direction

Remember: You are speaking to a real person seeking genuine guidance for their life. 
Let your responses be a light on their path."""


def ask_question(
    question: str, 
    traditions: Optional[List[str]] = None,
    conversation_history: Optional[List[Tuple[str, str]]] = None
):
    """
    Process a user's question and return spiritual guidance.
    
    Args:
        question: The user's question or concern
        traditions: List of religious traditions to draw from (None = all)
        conversation_history: Previous exchanges for context
    
    Returns:
        Tuple of (response text, retrieved documents)
    """
    docs = retrieve(question, traditions)
    context = context_to_text(docs)
    
    # Determine which traditions are represented in the retrieved docs
    traditions_in_context = list(set(
        d.metadata.get('tradition', 'Unknown') for d in docs
    ))
    
    system_prompt = get_advisor_system_prompt(traditions_in_context)
    
    # Build conversation context if available
    history_text = ""
    if conversation_history and len(conversation_history) > 0:
        recent_history = conversation_history[-3:]  # Last 3 exchanges
        history_parts = []
        for user_q, advisor_a in recent_history:
            history_parts.append(f"Seeker: {user_q}\nAdvisor: {advisor_a}")
        history_text = "\n\n".join(history_parts) + "\n\n"
    
    user_prompt = f"""SACRED WISDOM (from scriptures):
{context}

{f"PREVIOUS CONVERSATION:{chr(10)}{history_text}" if history_text else ""}

SEEKER'S QUESTION:
{question}

As their spiritual advisor, provide guidance that:
- Addresses their specific situation with empathy
- Draws relevant wisdom from the scripture passages above
- Offers practical direction they can apply to their life
- Leaves them with hope and clarity

Your guidance:"""

    llm = Ollama(model=OLLAMA_MODEL)
    
    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ])
    
    return response, docs


def get_available_traditions() -> List[str]:
    """Return list of traditions that have scriptures in the vectorstore."""
    db = get_vectorstore()
    try:
        # Sample some documents to see what traditions are available
        docs = db.similarity_search("wisdom guidance life", k=50)
        traditions = set()
        for d in docs:
            if 'tradition' in d.metadata:
                traditions.add(d.metadata['tradition'])
            elif 'book_title' in d.metadata:
                # Fallback for old-style metadata
                traditions.add(d.metadata['book_title'])
        return sorted(list(traditions))
    except Exception:
        return list(TRADITIONS.keys())
