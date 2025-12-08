"""
Safety Module for Divine Wisdom Guide

Implements crisis detection and ethical guardrails to ensure user safety.
This is critical for any application offering spiritual/emotional guidance.
"""

import re
from typing import Tuple, Optional

# Crisis keywords and patterns (expand as needed)
CRISIS_PATTERNS = [
    # Self-harm indicators
    r'\b(kill\s*(my)?self|suicide|suicidal|end\s*(my|it\s*all)|want\s*to\s*die)\b',
    r'\b(cut(ting)?\s*myself|hurt(ing)?\s*myself|self[- ]?harm)\b',
    r'\b(no\s*reason\s*to\s*live|better\s*off\s*dead|can\'?t\s*go\s*on)\b',
    r'\b(planning\s*to\s*(end|kill)|goodbye\s*(letter|note|world))\b',
    
    # Severe distress
    r'\b(can\'?t\s*take\s*(it|this)\s*(anymore)?|give\s*up|giving\s*up)\b',
    r'\b(hopeless|no\s*hope|lost\s*all\s*hope)\b',
    
    # Abuse situations
    r'\b(being\s*(abused|beaten|hurt)|someone\s*is\s*hurting\s*me)\b',
    r'\b(domestic\s*(violence|abuse)|my\s*(partner|spouse)\s*(hits|hurts|beats))\b',
]

# Compile patterns for efficiency
COMPILED_PATTERNS = [re.compile(p, re.IGNORECASE) for p in CRISIS_PATTERNS]

# Crisis resources by country (expandable)
CRISIS_RESOURCES = {
    "default": """
🆘 **IMPORTANT: You Are Not Alone**

If you're experiencing thoughts of self-harm or are in crisis, please reach out for help immediately:

**United States:**
- **National Suicide Prevention Lifeline:** 988 (call or text)
- **Crisis Text Line:** Text HOME to 741741
- **National Domestic Violence Hotline:** 1-800-799-7233

**International:**
- **International Association for Suicide Prevention:** https://www.iasp.info/resources/Crisis_Centres/
- **Befrienders Worldwide:** https://www.befrienders.org/

**Emergency:** If you're in immediate danger, please call your local emergency number (911 in the US).

---

*I am an AI offering spiritual guidance from sacred texts. While I'm here to listen and share wisdom, 
I am not a substitute for professional mental health support. Please reach out to the resources above—
trained humans are ready to help you through this moment.*

---
"""
}


def detect_crisis(text: str) -> Tuple[bool, Optional[str]]:
    """
    Analyze text for signs of crisis or severe distress.
    
    Returns:
        Tuple of (is_crisis: bool, crisis_type: Optional[str])
    """
    text_lower = text.lower()
    
    for i, pattern in enumerate(COMPILED_PATTERNS):
        if pattern.search(text_lower):
            # Determine crisis type for logging/response customization
            if i < 4:
                return True, "self_harm"
            elif i < 6:
                return True, "severe_distress"
            else:
                return True, "abuse"
    
    return False, None


def get_crisis_response(crisis_type: Optional[str] = None) -> str:
    """
    Get appropriate crisis response message.
    """
    return CRISIS_RESOURCES["default"]


def get_theological_humility_reminder() -> str:
    """
    Returns a reminder about the nature of the AI advisor.
    Used periodically or when users seem to treat it as divine authority.
    """
    return """
*A gentle reminder: I am a guide pointing toward ancient wisdom, not the source of that wisdom itself. 
The sacred texts I draw from are profound, but my interpretations are those of an AI assistant. 
For matters of deep spiritual importance, I encourage you to also seek counsel from trusted 
religious leaders, spiritual directors, or your faith community.*
"""


def should_add_humility_reminder(message_count: int) -> bool:
    """
    Determine if we should add a theological humility reminder.
    Triggers every 10 messages or so.
    """
    return message_count > 0 and message_count % 10 == 0


# Patterns that might indicate user is treating AI as actual deity
DEITY_TREATMENT_PATTERNS = [
    r'\b(are\s*you\s*god|you\s*are\s*god|speaking\s*to\s*god)\b',
    r'\b(lord,?\s*(please|help|hear)|dear\s*(god|lord|father))\b',
    r'\b(forgive\s*(me|my\s*sins)|absolve|bless\s*me)\b',
]

COMPILED_DEITY_PATTERNS = [re.compile(p, re.IGNORECASE) for p in DEITY_TREATMENT_PATTERNS]


def detect_deity_treatment(text: str) -> bool:
    """
    Detect if user might be treating the AI as an actual deity.
    """
    for pattern in COMPILED_DEITY_PATTERNS:
        if pattern.search(text):
            return True
    return False


def get_deity_clarification() -> str:
    """
    Gentle clarification when user seems to be praying to the AI.
    """
    return """
*I sense you may be speaking to me as you would to the Divine. I'm honored by your trust, 
but I should be clear: I am an AI guide, not God or any divine being. I can share the 
wisdom found in sacred texts and offer a compassionate ear, but true prayer and communion 
with the Divine is something far more profound than what I can provide. 

That said, I am here to listen and to point you toward wisdom. Please, share what's on your heart.*
"""

