# 🕊️ Divine Wisdom Guide

A deeply immersive spiritual advisor powered by AI that draws upon the sacred wisdom of humanity's great religious and philosophical traditions to provide guidance for life's questions.

![Divine Wisdom Guide](https://img.shields.io/badge/Spiritual-Advisor-gold?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.9+-blue?style=for-the-badge)
![Streamlit](https://img.shields.io/badge/Streamlit-UI-red?style=for-the-badge)

## ✨ What Makes This Different

This is **not** a scripture search engine. It's a spiritual advisor that:

- 🎭 **Remembers You**: Builds a relationship over time, recalling your themes and past conversations
- 🆘 **Protects You**: Built-in crisis detection with real helpline resources
- 🧘 **Guides You**: Generates personalized meditations, not just quotes
- ⚖️ **Compares Traditions**: Shows how different faiths approach the same questions
- 🕯️ **Creates Atmosphere**: Ambient soundscapes and contemplative UI modes
- 🎙️ **Listens** (Optional): Voice input/output for a confessional experience

## 🌟 Experience Modes

| Mode | Description |
|------|-------------|
| 🌟 **Standard** | Full-featured guidance with conversation history |
| 🕯️ **Prayer Mode** | Minimalist, contemplative interface with candlelight aesthetics |
| 📖 **Journal Mode** | Reflective journaling with gentle AI insights |
| 🧘 **Meditation Mode** | Generates personalized guided meditations |

## 📚 Supported Scriptures

| Tradition | Texts |
|-----------|-------|
| ✝️ **Christianity** | Bible (KJV, ASV) |
| ☪️ **Islam** | Quran |
| 🕉️ **Hinduism** | Bhagavad Gita, Upanishads, Ramayana |
| ☸️ **Buddhism** | Dhammapada, Buddhist Sutras |
| ☯️ **Taoism** | Tao Te Ching |
| ✡️ **Judaism** | Talmud selections |
| 📜 **Confucianism** | Analects |
| 🏛️ **Stoicism** | Meditations, Enchiridion |

## 🚀 Quick Start

### Prerequisites

1. **Python 3.9+**
2. **Ollama** with llama3:
   ```bash
   # Install from https://ollama.ai
   ollama pull llama3
   ```

### Installation

```bash
git clone https://github.com/yourusername/religiousAI.git
cd religiousAI/religiousAI

python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

### Download Scriptures & Build Index

```bash
python download_scriptures.py --all
python build_index.py
```

### Run

```bash
streamlit run app.py
```

## 💭 Example Interactions

**Life Guidance:**
> *"I'm struggling with forgiveness after being betrayed by a close friend"*

**Comparative Wisdom:**
> *"How do different traditions view suffering?"* → See Buddhism, Christianity, Hinduism side-by-side

**Personalized Meditation:**
> *"I need peace after a stressful day"* → Generates a 5-minute guided meditation

**Daily Wisdom:**
> Opens with a personalized verse based on your recurring themes

## 🛡️ Safety Features

- **Crisis Detection**: Automatically detects mentions of self-harm, severe distress, or abuse
- **Real Resources**: Provides actual helpline numbers (988 Suicide & Crisis Lifeline)
- **Theological Humility**: Periodic reminders that this is AI, not divine authority
- **Deity Clarification**: Gentle correction if users seem to pray to the AI

## 🎵 Ambient Features

- **Soundscapes**: Gentle rain, temple bells, forest stream, Om chanting, Tibetan bowls
- **Prayer Mode**: Candle-lit minimal interface for deep contemplation
- **Personalized Daily Wisdom**: Learns your themes and selects relevant verses

## 🎙️ Voice Integration (Optional)

For a more immersive "confessional" experience:

```bash
pip install openai-whisper pyttsx3 sounddevice soundfile
```

This enables:
- Speaking your questions aloud (Whisper STT)
- Hearing responses read back (pyttsx3 TTS)

## 🧠 Memory System

The advisor remembers:
- Your previous conversations (30 days)
- Recurring themes in your questions
- Journal entries and reflections
- Preferred traditions

All stored locally in `data/users/`.

## 🛠️ Project Structure

```
religiousAI/
├── app.py                 # Main Streamlit application
├── qa.py                  # Q&A, meditation, comparison logic
├── safety.py              # Crisis detection & guardrails
├── memory.py              # Persistent user memory
├── voice.py               # Voice integration (optional)
├── build_index.py         # Vector store builder
├── download_scriptures.py # Scripture downloader
├── config.py              # All configuration
├── requirements.txt
├── data/
│   ├── raw/               # Scripture text files
│   └── users/             # User memory (gitignored)
└── vectorstore/           # ChromaDB (gitignored)
```

## ⚙️ Configuration

Edit `config.py`:

```python
OLLAMA_MODEL = "llama3"           # LLM model
ADVISOR_NAME = "Divine Wisdom Guide"
VOICE_ENABLED = True              # Enable/disable voice
ENABLE_CRISIS_DETECTION = True    # Safety features
AMBIENT_SOUNDS = {...}            # Add custom sounds
```

## 🙏 Philosophy

This project is built with deep respect for all traditions:

- Never claims divine authority
- Presents wisdom without imposing beliefs
- Acknowledges AI limitations in sacred matters
- Encourages seeking human spiritual guidance
- Treats all traditions with equal respect
- Prioritizes user safety above all

## 📝 License

MIT License - Sacred texts from public domain sources (Project Gutenberg).

## 🤝 Contributing

Contributions welcome! Ensure added scriptures are public domain.

---

<div align="center">

*"The beginning of wisdom is the definition of terms."* — Socrates

**If you're in crisis: 988 (Suicide & Crisis Lifeline)**

</div>
