import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

RAW_DATA_DIR = os.path.join(BASE_DIR, "data", "raw")
VECTORSTORE_DIR = os.path.join(BASE_DIR, "vectorstore")
USER_DATA_DIR = os.path.join(BASE_DIR, "data", "users")  # For conversation memory

EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

# Use llama3 in Ollama
OLLAMA_MODEL = "llama3"

# ----------------------- Scripture Traditions -----------------------
TRADITIONS = {
    "Christianity": {
        "color": "#C9A227",
        "icon": "✝️",
        "scriptures": ["bible_kjv.txt", "bible_niv.txt", "bible_asv.txt"],
        "description": "The Holy Bible - Old and New Testaments"
    },
    "Islam": {
        "color": "#2E7D32",
        "icon": "☪️",
        "scriptures": ["quran.txt"],
        "description": "The Holy Quran - Words of Allah revealed to Prophet Muhammad"
    },
    "Hinduism": {
        "color": "#FF6F00",
        "icon": "🕉️",
        "scriptures": ["bhagavad_gita.txt", "upanishads.txt", "ramayana.txt"],
        "description": "Bhagavad Gita, Upanishads - Ancient wisdom of dharma"
    },
    "Buddhism": {
        "color": "#FFD54F",
        "icon": "☸️",
        "scriptures": ["dhammapada.txt", "heart_sutra.txt", "buddhist_sutras.txt"],
        "description": "Dhammapada, Sutras - Teachings of the Buddha"
    },
    "Taoism": {
        "color": "#424242",
        "icon": "☯️",
        "scriptures": ["tao_te_ching.txt"],
        "description": "Tao Te Ching - The way of harmony and balance"
    },
    "Judaism": {
        "color": "#1565C0",
        "icon": "✡️",
        "scriptures": ["torah.txt", "talmud_selections.txt"],
        "description": "Torah, Talmud - The covenant and wisdom of Israel"
    },
    "Sikhism": {
        "color": "#FF8F00",
        "icon": "🙏",
        "scriptures": ["guru_granth_sahib.txt"],
        "description": "Guru Granth Sahib - Teachings of the Sikh Gurus"
    },
    "Stoicism": {
        "color": "#5D4037",
        "icon": "🏛️",
        "scriptures": ["meditations_aurelius.txt", "enchiridion.txt"],
        "description": "Meditations, Enchiridion - Ancient philosophical wisdom"
    },
    "Confucianism": {
        "color": "#7B1FA2",
        "icon": "📜",
        "scriptures": ["analects.txt"],
        "description": "Analects - Teachings of Confucius on virtue and society"
    },
}

# ----------------------- Advisor Persona -----------------------
ADVISOR_NAME = "Divine Wisdom Guide"
ADVISOR_GREETING = """
Welcome, seeker. I am here to offer guidance drawn from the sacred wisdom 
of humanity's great spiritual traditions. Share with me what weighs upon 
your heart, and together we shall find light for your path.
"""

# ----------------------- Ambient Soundscapes -----------------------
# These are free ambient sound URLs (using freesound.org or similar)
AMBIENT_SOUNDS = {
    "Silence": None,
    "Gentle Rain": "https://cdn.pixabay.com/audio/2022/05/16/audio_1808fbf07a.mp3",
    "Temple Bells": "https://cdn.pixabay.com/audio/2022/10/30/audio_ff329c14a8.mp3",
    "Forest Stream": "https://cdn.pixabay.com/audio/2021/08/04/audio_0625c1539c.mp3",
    "Om Chanting": "https://cdn.pixabay.com/audio/2022/03/15/audio_8cb749d484.mp3",
    "Tibetan Bowls": "https://cdn.pixabay.com/audio/2022/01/18/audio_d0a13f69d2.mp3",
}

# ----------------------- UI Modes -----------------------
UI_MODES = {
    "standard": {
        "name": "Standard",
        "description": "Full interface with all features",
        "icon": "🌟"
    },
    "prayer": {
        "name": "Prayer Mode",
        "description": "Minimalist, contemplative interface",
        "icon": "🕯️"
    },
    "journal": {
        "name": "Journal Mode", 
        "description": "Reflective journaling with gentle insights",
        "icon": "📖"
    },
    "meditation": {
        "name": "Meditation Mode",
        "description": "Guided meditations based on your needs",
        "icon": "🧘"
    }
}

# ----------------------- Voice Settings -----------------------
VOICE_ENABLED = True  # Set to False to disable voice features
TTS_VOICE = "slow"  # Options: slow, calm, warm
STT_MODEL = "base"  # Whisper model: tiny, base, small, medium, large

# ----------------------- Safety Settings -----------------------
ENABLE_CRISIS_DETECTION = True
SHOW_HUMILITY_REMINDER_EVERY = 10  # messages
