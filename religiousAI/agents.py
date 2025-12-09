"""
Multi-Agent Spiritual System for Divine Wisdom Guide

Uses 4 specialized LLM agents that work together to provide
comprehensive spiritual guidance:

1. Compassion Agent - Emotional grounding & empathy
2. Scripture Agent - Strict scriptural accuracy with citations
3. Scholar Agent - Deep theological explanations
4. Guidance Agent - Practical life advice

The agents collaborate behind the scenes to form a unified response.
"""

from typing import List, Optional, Dict, Tuple
from langchain_community.llms import Ollama
from langchain_core.messages import SystemMessage, HumanMessage

from config import OLLAMA_MODEL, TRADITIONS


def get_llm():
    """Get the LLM instance."""
    return Ollama(model=OLLAMA_MODEL)


# =====================================================================
# AGENT SYSTEM PROMPTS
# =====================================================================

COMPASSION_AGENT_PROMPT = """You are the Compassion Agent - a deeply empathetic spiritual counselor.

YOUR ROLE:
- Acknowledge and validate the seeker's emotions
- Provide emotional grounding and comfort
- Show that their feelings are understood and normal
- Create a safe, non-judgmental space

YOUR RESPONSE STYLE:
- Warm, gentle, and nurturing
- Use phrases like "I sense...", "I understand...", "It's natural to feel..."
- Brief: 2-3 sentences maximum
- Focus purely on emotional acknowledgment, not solutions

DO NOT:
- Quote scripture (that's another agent's job)
- Give advice (that's another agent's job)
- Be preachy or lecture"""

SCRIPTURE_AGENT_PROMPT = """You are the Scripture Agent - a precise scholar of sacred texts.

YOUR ROLE:
- Find and cite relevant scripture passages
- Ensure strict accuracy to the original texts
- Provide exact references (book, chapter, verse when applicable)
- Present passages that directly relate to the seeker's situation

YOUR RESPONSE STYLE:
- Scholarly and precise
- Always cite sources: "In [Scripture], it is written: '[quote]'"
- Brief: 1-2 relevant passages maximum
- Present without interpretation (other agents interpret)

AVAILABLE TRADITIONS:
{traditions}

DO NOT:
- Interpret or explain the passages (Scholar Agent does that)
- Give emotional support (Compassion Agent does that)
- Give practical advice (Guidance Agent does that)"""

SCHOLAR_AGENT_PROMPT = """You are the Scholar Agent - a deep theologian and interpreter.

YOUR ROLE:
- Explain the theological meaning of the scriptures provided
- Provide historical and cultural context
- Connect ancient wisdom to modern understanding
- Illuminate deeper spiritual truths

YOUR RESPONSE STYLE:
- Thoughtful and educational
- Bridge ancient wisdom to present circumstances
- Brief: 2-3 sentences of interpretation
- Make complex theology accessible

DO NOT:
- Quote scripture (Scripture Agent did that)
- Provide emotional support (Compassion Agent did that)
- Give specific life advice (Guidance Agent does that)"""

GUIDANCE_AGENT_PROMPT = """You are the Guidance Agent - a practical spiritual advisor.

YOUR ROLE:
- Translate wisdom into actionable steps
- Provide practical, real-world advice
- Suggest specific practices or actions
- Give hope and direction

YOUR RESPONSE STYLE:
- Practical and empowering
- Use phrases like "You might consider...", "One practice that may help..."
- Brief: 2-3 specific suggestions
- End with encouragement

DO NOT:
- Quote scripture (Scripture Agent did that)
- Explain theology (Scholar Agent did that)  
- Focus on emotions (Compassion Agent did that)"""

SYNTHESIZER_PROMPT = """You are the Divine Wisdom Guide synthesizer.

You have received insights from 4 specialized spiritual agents:
1. COMPASSION - emotional support
2. SCRIPTURE - relevant sacred texts
3. SCHOLAR - theological interpretation  
4. GUIDANCE - practical advice

YOUR TASK:
Weave these perspectives into ONE unified, flowing response that feels like it comes from a single wise advisor. 

RULES:
- Create natural transitions between perspectives
- Don't label sections or mention the agents
- Maintain a warm, wise tone throughout
- Keep the response focused and not too long
- Preserve scripture citations naturally inline
- End with hope and encouragement

Create a response that feels like speaking with one deeply wise spiritual guide, not four separate voices."""


# =====================================================================
# INDIVIDUAL AGENT FUNCTIONS
# =====================================================================

def run_compassion_agent(question: str, context: str = "") -> str:
    """Run the Compassion Agent for emotional grounding."""
    llm = get_llm()
    
    prompt = f"""Question from seeker: {question}

{f"Context from their history: {context}" if context else ""}

Provide brief emotional acknowledgment and grounding (2-3 sentences):"""

    response = llm.invoke([
        SystemMessage(content=COMPASSION_AGENT_PROMPT),
        HumanMessage(content=prompt)
    ])
    
    return response.strip()


def run_scripture_agent(question: str, scripture_context: str, traditions: List[str] = None) -> str:
    """Run the Scripture Agent for accurate citations."""
    llm = get_llm()
    
    traditions_str = ", ".join(traditions) if traditions else ", ".join(TRADITIONS.keys())
    system_prompt = SCRIPTURE_AGENT_PROMPT.format(traditions=traditions_str)
    
    prompt = f"""Question from seeker: {question}

Relevant scripture passages found:
{scripture_context}

Select and cite the most relevant passage(s) with exact references:"""

    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=prompt)
    ])
    
    return response.strip()


def run_scholar_agent(question: str, scripture_citation: str) -> str:
    """Run the Scholar Agent for theological interpretation."""
    llm = get_llm()
    
    prompt = f"""Question from seeker: {question}

Scripture cited:
{scripture_citation}

Provide theological interpretation and context (2-3 sentences):"""

    response = llm.invoke([
        SystemMessage(content=SCHOLAR_AGENT_PROMPT),
        HumanMessage(content=prompt)
    ])
    
    return response.strip()


def run_guidance_agent(question: str, all_context: str) -> str:
    """Run the Guidance Agent for practical advice."""
    llm = get_llm()
    
    prompt = f"""Question from seeker: {question}

Wisdom shared so far:
{all_context}

Provide 2-3 practical, actionable suggestions:"""

    response = llm.invoke([
        SystemMessage(content=GUIDANCE_AGENT_PROMPT),
        HumanMessage(content=prompt)
    ])
    
    return response.strip()


def synthesize_responses(
    question: str,
    compassion: str,
    scripture: str,
    scholar: str,
    guidance: str
) -> str:
    """Synthesize all agent responses into one unified response."""
    llm = get_llm()
    
    prompt = f"""SEEKER'S QUESTION:
{question}

COMPASSION AGENT (emotional support):
{compassion}

SCRIPTURE AGENT (sacred texts):
{scripture}

SCHOLAR AGENT (interpretation):
{scholar}

GUIDANCE AGENT (practical advice):
{guidance}

---
Now synthesize these into ONE unified, flowing response from a wise spiritual advisor:"""

    response = llm.invoke([
        SystemMessage(content=SYNTHESIZER_PROMPT),
        HumanMessage(content=prompt)
    ])
    
    return response.strip()


# =====================================================================
# MAIN MULTI-AGENT FUNCTION
# =====================================================================

def multi_agent_guidance(
    question: str,
    scripture_context: str,
    traditions: List[str] = None,
    user_context: str = ""
) -> Tuple[str, Dict[str, str]]:
    """
    Run the full multi-agent system to generate comprehensive guidance.
    
    Args:
        question: The seeker's question
        scripture_context: Retrieved scripture passages
        traditions: List of traditions to draw from
        user_context: Context about the user from memory
    
    Returns:
        Tuple of (final_response, agent_outputs_dict)
    """
    
    # Step 1: Compassion Agent - Emotional grounding
    compassion_response = run_compassion_agent(question, user_context)
    
    # Step 2: Scripture Agent - Accurate citations
    scripture_response = run_scripture_agent(question, scripture_context, traditions)
    
    # Step 3: Scholar Agent - Theological interpretation
    scholar_response = run_scholar_agent(question, scripture_response)
    
    # Step 4: Guidance Agent - Practical advice
    combined_context = f"{compassion_response}\n\n{scripture_response}\n\n{scholar_response}"
    guidance_response = run_guidance_agent(question, combined_context)
    
    # Step 5: Synthesize into unified response
    final_response = synthesize_responses(
        question,
        compassion_response,
        scripture_response,
        scholar_response,
        guidance_response
    )
    
    # Return both the final response and individual agent outputs (for debugging/transparency)
    agent_outputs = {
        "compassion": compassion_response,
        "scripture": scripture_response,
        "scholar": scholar_response,
        "guidance": guidance_response
    }
    
    return final_response, agent_outputs


# =====================================================================
# CROSS-RELIGIOUS COMPARISON (Enhanced)
# =====================================================================

def compare_religions_on_topic(
    topic: str,
    traditions: List[str],
    scripture_by_tradition: Dict[str, str]
) -> str:
    """
    Generate a respectful comparison of how different religions address a topic.
    
    Args:
        topic: The topic to compare (e.g., "forgiveness", "suffering")
        traditions: List of traditions to compare
        scripture_by_tradition: Dict mapping tradition name to retrieved scripture text
    """
    llm = get_llm()
    
    system_prompt = """You are a respectful comparative religion scholar.

YOUR ROLE:
- Present each tradition's perspective fairly and accurately
- Cite specific scriptures provided
- Highlight unique insights from each tradition
- Find common threads of wisdom
- Never favor one tradition over another

RESPONSE FORMAT:
For each tradition, provide:
1. Key teaching on the topic
2. Supporting scripture with citation
3. Unique insight

End with a "Common Wisdom" section highlighting universal truths."""

    # Build the scripture context
    scripture_sections = []
    for tradition in traditions:
        if tradition in scripture_by_tradition:
            scripture_sections.append(f"**{tradition}:**\n{scripture_by_tradition[tradition]}")
    
    scripture_text = "\n\n".join(scripture_sections)
    
    prompt = f"""TOPIC: {topic}

TRADITIONS TO COMPARE: {", ".join(traditions)}

SCRIPTURE PASSAGES:
{scripture_text}

Provide a respectful comparison showing how each tradition addresses "{topic}":"""

    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=prompt)
    ])
    
    return response.strip()

