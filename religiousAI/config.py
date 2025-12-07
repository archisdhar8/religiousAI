import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

RAW_DATA_DIR = os.path.join(BASE_DIR, "data", "raw")
VECTORSTORE_DIR = os.path.join(BASE_DIR, "vectorstore")

EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

# Use llama3 in Ollama
OLLAMA_MODEL = "llama3"

# ----------------------- Scripture Traditions -----------------------
# Maps tradition names to their scripture files and display info
TRADITIONS = {
    "Christianity": {
        "color": "#C9A227",  # Gold
        "icon": "✝️",
        "scriptures": ["bible_kjv.txt", "bible_niv.txt"],
        "description": "The Holy Bible - Old and New Testaments"
    },
    "Islam": {
        "color": "#2E7D32",  # Green
        "icon": "☪️",
        "scriptures": ["quran.txt"],
        "description": "The Holy Quran - Words of Allah revealed to Prophet Muhammad"
    },
    "Hinduism": {
        "color": "#FF6F00",  # Saffron
        "icon": "🕉️",
        "scriptures": ["bhagavad_gita.txt", "upanishads.txt"],
        "description": "Bhagavad Gita, Upanishads - Ancient wisdom of dharma"
    },
    "Buddhism": {
        "color": "#FFD54F",  # Gold/Yellow
        "icon": "☸️",
        "scriptures": ["dhammapada.txt", "heart_sutra.txt"],
        "description": "Dhammapada, Sutras - Teachings of the Buddha"
    },
    "Taoism": {
        "color": "#424242",  # Dark grey
        "icon": "☯️",
        "scriptures": ["tao_te_ching.txt"],
        "description": "Tao Te Ching - The way of harmony and balance"
    },
    "Judaism": {
        "color": "#1565C0",  # Blue
        "icon": "✡️",
        "scriptures": ["torah.txt", "talmud_selections.txt"],
        "description": "Torah, Talmud - The covenant and wisdom of Israel"
    },
    "Sikhism": {
        "color": "#FF8F00",  # Orange
        "icon": "🙏",
        "scriptures": ["guru_granth_sahib.txt"],
        "description": "Guru Granth Sahib - Teachings of the Sikh Gurus"
    },
}

# Advisor persona settings
ADVISOR_NAME = "Divine Wisdom Guide"
ADVISOR_GREETING = """
Welcome, seeker. I am here to offer guidance drawn from the sacred wisdom 
of humanity's great spiritual traditions. Share with me what weighs upon 
your heart, and together we shall find light for your path.
"""
