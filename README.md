# 🕊️ Divine Wisdom Guide

A deeply immersive spiritual advisor powered by AI that draws upon the sacred wisdom of humanity's great religious and philosophical traditions to provide guidance for life's questions.

![Divine Wisdom Guide](https://img.shields.io/badge/Spiritual-Advisor-gold?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.9+-blue?style=for-the-badge)
![React](https://img.shields.io/badge/React-18+-blue?style=for-the-badge)
![Supabase](https://img.shields.io/badge/Supabase-Database-green?style=for-the-badge)

## ✨ What Makes This Different

This is **not** a scripture search engine. It's a spiritual advisor that:

- 🎭 **Remembers You**: Builds a relationship over time, recalling your themes and past conversations
- 🆘 **Protects You**: Built-in crisis detection with real helpline resources
- 🧘 **Guides You**: Generates personalized meditations, not just quotes
- ⚖️ **Compares Traditions**: Shows how different faiths approach the same questions
- 🕯️ **Creates Atmosphere**: Ambient soundscapes and contemplative UI modes
- 👥 **Community**: Connect with others on similar spiritual journeys
- 🔒 **Secure**: Built on Supabase with enterprise-grade security

## 🏗️ Architecture Overview

The application consists of three main components:

```
┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
│   React UI      │────────▶│   FastAPI       │────────▶│   Supabase      │
│   (Frontend)    │  HTTP   │   (Backend)     │  REST   │   (Database)    │
│   Port 8080     │         │   Port 8000     │         │   PostgreSQL    │
└─────────────────┘         └─────────────────┘         └─────────────────┘
                                      │
                                      ▼
                            ┌─────────────────┐
                            │   Ollama LLM    │
                            │   (llama3)      │
                            └─────────────────┘
```

### Components

1. **Frontend** (`divine-dialogue-main/`): React + TypeScript application
   - Modern, responsive UI
   - Real-time chat interface
   - Community features
   - Authentication

2. **Backend** (`religiousAI/`): FastAPI Python server
   - REST API endpoints
   - AI/LLM integration (Ollama)
   - Vector search (ChromaDB)
   - Business logic

3. **Database** (Supabase): PostgreSQL database
   - User authentication
   - Data storage (chats, memory, profiles)
   - Real-time subscriptions
   - Row-level security

## 🚀 Quick Start

### Prerequisites

1. **Python 3.9+** with virtual environment
2. **Node.js 18+** and npm
3. **Ollama** with llama3 model:
   ```bash
   ollama pull llama3
   ```
4. **Supabase Account** (free tier works)

### Installation

#### 1. Clone the Repository

```bash
git clone <repository-url>
cd religiousAI
```

#### 2. Backend Setup

```bash
cd religiousAI

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download scriptures and build vector index
python download_scriptures.py --all
python build_index.py
```

#### 3. Supabase Setup

1. Create a Supabase project at https://supabase.com
2. Get your project URL and API keys
3. Create `.env` file in `religiousAI/`:
   ```env
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_ANON_KEY=your-anon-key
   SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
   ```
4. Run the database schema:
   - Go to Supabase Dashboard → SQL Editor
   - Copy and paste contents of `religiousAI/db_schema.sql`
   - Click Run

See [SUPABASE_SETUP.md](./SUPABASE_SETUP.md) for detailed instructions.

#### 4. Frontend Setup

```bash
cd divine-dialogue-main

# Install dependencies
npm install

# Create .env file (optional, defaults to http://localhost:8000)
echo "VITE_API_URL=http://localhost:8000" > .env
```

### Running the Application

You need to run both servers:

**Terminal 1 - Backend:**
```bash
cd religiousAI
source venv/bin/activate
uvicorn api:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd divine-dialogue-main
npm run dev
```

**Access the application:**
- Frontend: http://localhost:8080
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

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

## 🧠 Key Features

### Memory & Personalization
- Remembers past conversations
- Tracks recurring themes
- Builds personality insights
- Personalized greetings for returning users

### Multiple Chat Threads
- Create separate conversations
- Organize by topic or religion
- Switch between chats easily
- Auto-generate chat titles

### Community Features
- Create spiritual profiles
- Find compatible companions
- Send connection requests
- Build a spiritual community

### Search & Discovery
- Full-text search in chats
- Search journal entries
- Find community members
- Discover shared interests

## 📁 Project Structure

```
religiousAI/
├── Backend (Python/FastAPI)
│   ├── api.py                 # FastAPI server & endpoints
│   ├── auth.py                # Authentication (Supabase)
│   ├── memory.py              # User memory management
│   ├── community.py           # Community features
│   ├── qa.py                  # AI Q&A logic
│   ├── safety.py              # Crisis detection
│   ├── agents.py              # Multi-agent system
│   ├── supabase_client.py     # Supabase client
│   ├── search.py              # Full-text search
│   ├── supabase_realtime.py   # Real-time features
│   ├── config.py              # Configuration
│   ├── db_schema.sql          # Database schema
│   └── migrate_data.py        # Data migration script
│
├── Frontend (React/TypeScript)
│   └── divine-dialogue-main/
│       ├── src/
│       │   ├── pages/         # Page components
│       │   ├── components/    # UI components
│       │   └── lib/           # API client
│       └── package.json
│
└── Data
    ├── data/raw/              # Scripture text files
    └── vectorstore/           # ChromaDB embeddings
```

## 📖 Documentation

- **[QUICKSTART.md](./QUICKSTART.md)** - Get started in 10 minutes ⚡
- **[INTEGRATION.md](./INTEGRATION.md)** - Detailed setup guide for React + FastAPI
- **[SUPABASE_SETUP.md](./SUPABASE_SETUP.md)** - Complete Supabase integration guide
- **[ARCHITECTURE.md](./ARCHITECTURE.md)** - System architecture and design decisions
- **[API Documentation](http://localhost:8000/docs)** - Interactive API docs (when server is running)

## ⚙️ Configuration

### Backend Configuration (`config.py`)

```python
USE_SUPABASE = True              # Use Supabase (True) or file-based (False)
OLLAMA_MODEL = "llama3"          # LLM model
ENABLE_CRISIS_DETECTION = True   # Safety features
```

### Environment Variables (`.env`)

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
```

### Frontend Configuration (`.env`)

```env
VITE_API_URL=http://localhost:8000
```

## 🔄 Data Migration

If you have existing JSON data files:

```bash
cd religiousAI
source venv/bin/activate
python migrate_data.py
```

This will migrate users, conversations, and profiles to Supabase. See [SUPABASE_SETUP.md](./SUPABASE_SETUP.md) for details.

## 🐛 Troubleshooting

### Backend Issues

**"Module not found: supabase"**
```bash
pip install supabase python-dotenv
```

**"Table does not exist"**
- Make sure you ran `db_schema.sql` in Supabase SQL Editor

**"Connection failed"**
- Check `.env` file has correct Supabase credentials
- Verify Supabase project is active

### Frontend Issues

**CORS Errors**
- Ensure backend is running on port 8000
- Check CORS settings in `api.py`

**Can't connect to API**
- Verify `VITE_API_URL` in frontend `.env`
- Check backend is running: `curl http://localhost:8000/`

### Ollama Issues

**"Ollama connection failed"**
- Make sure Ollama is running: `ollama list`
- Verify llama3 model is installed: `ollama pull llama3`

## 🚀 Production Deployment

### Backend
- Use Gunicorn with Uvicorn workers
- Set up environment variables securely
- Configure CORS for production domain

### Frontend
- Build static files: `npm run build`
- Serve with nginx or similar
- Update `VITE_API_URL` to production API

### Supabase
- Use production database
- Configure RLS policies
- Set up backups
- Monitor usage

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
