# Integration Guide: React Frontend + FastAPI Backend

Complete guide for setting up and running the integrated application.

## 📋 Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Prerequisites](#prerequisites)
3. [Backend Setup](#backend-setup)
4. [Frontend Setup](#frontend-setup)
5. [Running the Application](#running-the-application)
6. [API Endpoints](#api-endpoints)
7. [Configuration](#configuration)
8. [Troubleshooting](#troubleshooting)

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        User's Browser                        │
│  ┌──────────────────────────────────────────────────────┐   │
│  │         React Frontend (Port 8080)                   │   │
│  │  - Chat Interface                                    │   │
│  │  - Authentication                                    │   │
│  │  - Community Features                                │   │
│  └──────────────────┬───────────────────────────────────┘   │
└─────────────────────┼───────────────────────────────────────┘
                      │ HTTP/REST API
                      ▼
┌─────────────────────────────────────────────────────────────┐
│              FastAPI Backend (Port 8000)                     │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  API Endpoints                                       │   │
│  │  - /api/chat                                         │   │
│  │  - /api/auth/*                                       │   │
│  │  - /api/community/*                                  │   │
│  └──────┬───────────────────────┬───────────────────────┘   │
│         │                       │                            │
│         ▼                       ▼                            │
│  ┌─────────────┐      ┌──────────────────┐                 │
│  │   Ollama    │      │    Supabase      │                 │
│  │   (llama3)  │      │   PostgreSQL     │                 │
│  └─────────────┘      └──────────────────┘                 │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

1. **User sends message** → Frontend → Backend API
2. **Backend processes** → Queries vector store → Calls Ollama LLM
3. **Response generated** → Saved to Supabase → Returned to frontend
4. **Frontend displays** → Updates UI → Stores in local state

## 📦 Prerequisites

### Required

1. **Python 3.9+**
   ```bash
   python --version  # Should be 3.9 or higher
   ```

2. **Node.js 18+**
   ```bash
   node --version  # Should be 18 or higher
   ```

3. **Ollama with llama3**
   ```bash
   # Install Ollama from https://ollama.ai
   ollama pull llama3
   ollama list  # Verify llama3 is installed
   ```

4. **Supabase Account**
   - Sign up at https://supabase.com (free tier works)
   - Create a new project
   - Get your project URL and API keys

### Optional

- **Git** for version control
- **VS Code** or your preferred IDE

## 🔧 Backend Setup

### Step 1: Navigate to Backend Directory

```bash
cd religiousAI
```

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

You should see `(venv)` in your terminal prompt.

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- FastAPI (web framework)
- Supabase (database client)
- LangChain (AI framework)
- ChromaDB (vector store)
- And other dependencies

### Step 4: Download Scriptures

```bash
python download_scriptures.py --all
```

This downloads all scripture text files to `data/raw/`.

### Step 5: Build Vector Index

```bash
python build_index.py
```

This creates embeddings and stores them in `vectorstore/`. This may take a few minutes.

### Step 6: Configure Supabase

1. Create `.env` file in `religiousAI/`:
   ```env
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_ANON_KEY=your-anon-key-here
   SUPABASE_SERVICE_ROLE_KEY=your-service-role-key-here
   ```

2. Run the database schema:
   - Go to Supabase Dashboard → SQL Editor
   - Copy contents of `db_schema.sql`
   - Paste and run

See [SUPABASE_SETUP.md](./SUPABASE_SETUP.md) for detailed Supabase setup.

### Step 7: Verify Backend Setup

```bash
# Start the server
uvicorn api:app --reload --port 8000

# In another terminal, test it:
curl http://localhost:8000/
```

You should see a JSON response with API status.

## 🎨 Frontend Setup

### Step 1: Navigate to Frontend Directory

```bash
cd divine-dialogue-main
```

### Step 2: Install Dependencies

```bash
npm install
```

This installs React, TypeScript, and all UI dependencies.

### Step 3: Configure API URL

Create `.env` file in `divine-dialogue-main/`:

```env
VITE_API_URL=http://localhost:8000
```

**Note:** For production, change this to your production API URL.

### Step 4: Verify Frontend Setup

```bash
npm run dev
```

You should see the app running at http://localhost:8080

## 🚀 Running the Application

You need **two terminal windows** running simultaneously:

### Terminal 1: Backend Server

```bash
cd religiousAI
source venv/bin/activate  # or: venv\Scripts\activate on Windows
uvicorn api:app --reload --port 8000
```

**Expected output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

### Terminal 2: Frontend Server

```bash
cd divine-dialogue-main
npm run dev
```

**Expected output:**
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:8080/
  ➜  Network: use --host to expose
```

### Access the Application

- **Frontend UI**: http://localhost:8080
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs (Swagger UI)
- **Alternative API Docs**: http://localhost:8000/redoc

## 📡 API Endpoints

### Authentication

- `POST /api/auth/signup` - Create new user account
- `POST /api/auth/login` - Login with email/password
- `POST /api/auth/logout` - Logout current user
- `GET /api/auth/me` - Get current user info

### Chat

- `POST /api/chat` - Send message and get AI response
- `GET /api/chats` - Get all chat conversations
- `POST /api/chats` - Create new chat
- `GET /api/chats/{chat_id}` - Get specific chat
- `PUT /api/chats/{chat_id}` - Rename chat
- `DELETE /api/chats/{chat_id}` - Delete chat

### Wisdom & Guidance

- `GET /api/daily-wisdom` - Get personalized daily wisdom
- `POST /api/compare` - Compare traditions on a topic
- `POST /api/journal` - Submit journal entry for reflection
- `GET /api/greeting` - Get personalized greeting

### Community

- `POST /api/community/profile` - Create/update profile
- `GET /api/community/profile` - Get user's profile
- `GET /api/community/matches` - Find compatible users
- `POST /api/community/connect` - Send connection request
- `GET /api/community/connections` - Get connections list

### Utilities

- `GET /api/traditions` - Get available traditions
- `GET /` - Health check

**Full API Documentation**: Visit http://localhost:8000/docs when the backend is running.

## ⚙️ Configuration

### Backend Configuration

Edit `religiousAI/config.py`:

```python
USE_SUPABASE = True              # Use Supabase (recommended)
OLLAMA_MODEL = "llama3"          # LLM model name
ENABLE_CRISIS_DETECTION = True   # Enable safety features
```

### Environment Variables

**Backend** (`religiousAI/.env`):
```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
```

**Frontend** (`divine-dialogue-main/.env`):
```env
VITE_API_URL=http://localhost:8000
```

### CORS Configuration

CORS is configured in `api.py`. For production, update allowed origins:

```python
allow_origins=[
    "https://your-production-domain.com",
    # ... other allowed origins
]
```

## 🐛 Troubleshooting

### Backend Won't Start

**Error: "Address already in use"**
```bash
# Find process using port 8000
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Kill the process or use a different port
uvicorn api:app --reload --port 8001
```

**Error: "Module not found"**
```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

**Error: "Ollama connection failed"**
```bash
# Check Ollama is running
ollama list

# If not running, start it
ollama serve
```

### Frontend Won't Start

**Error: "Port 8080 already in use"**
```bash
# Use a different port
npm run dev -- --port 8081
```

**Error: "Cannot connect to API"**
- Verify backend is running: `curl http://localhost:8000/`
- Check `VITE_API_URL` in `.env` file
- Check browser console for specific errors

### CORS Errors

If you see CORS errors in the browser console:

1. Verify backend is running
2. Check `allow_origins` in `api.py` includes `http://localhost:8080`
3. Clear browser cache and reload

### Authentication Issues

**"Invalid token" errors:**
- User session may have expired
- Try logging out and logging back in
- Check Supabase dashboard for auth issues

**"User not found" errors:**
- Verify user exists in Supabase
- Check RLS policies are configured correctly

### Data Not Appearing

**Chats not showing:**
- Verify Supabase schema is applied
- Check browser console for errors
- Verify user is authenticated

**Messages not saving:**
- Check Supabase connection
- Verify RLS policies allow writes
- Check backend logs for errors

## 🔍 Development Tips

### Hot Reload

Both servers support hot reload:
- **Backend**: Automatically reloads on file changes (thanks to `--reload`)
- **Frontend**: Vite automatically reloads on file changes

### Debugging

**Backend:**
- Check terminal output for errors
- Visit http://localhost:8000/docs for API testing
- Add print statements or use a debugger

**Frontend:**
- Use browser DevTools (F12)
- Check Console tab for errors
- Check Network tab for API calls
- Use React DevTools extension

### Testing API Endpoints

Use the interactive Swagger UI:
1. Start backend server
2. Visit http://localhost:8000/docs
3. Click "Try it out" on any endpoint
4. Fill in parameters and execute

### Database Inspection

1. Go to Supabase Dashboard
2. Navigate to Table Editor
3. Browse tables and data
4. Use SQL Editor for custom queries

## 📚 Next Steps

1. ✅ Backend and frontend are running
2. ✅ Test authentication (sign up, log in)
3. ✅ Test chat functionality
4. ✅ Explore community features
5. ✅ Read [SUPABASE_SETUP.md](./SUPABASE_SETUP.md) for database details

## 🚀 Production Deployment

### Backend

1. Use production ASGI server:
   ```bash
   pip install gunicorn
   gunicorn api:app -w 4 -k uvicorn.workers.UvicornWorker
   ```

2. Set up reverse proxy (nginx)
3. Configure environment variables securely
4. Set up SSL/TLS certificates

### Frontend

1. Build production bundle:
   ```bash
   npm run build
   ```

2. Serve `dist/` directory with nginx or similar
3. Update `VITE_API_URL` to production API URL

### Supabase

1. Use production database
2. Configure backups
3. Set up monitoring
4. Review RLS policies

---

For Supabase-specific setup, see [SUPABASE_SETUP.md](./SUPABASE_SETUP.md).
