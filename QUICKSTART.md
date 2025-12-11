# Quick Start Guide

Get up and running with Divine Wisdom Guide in 10 minutes.

## Prerequisites Checklist

- [ ] Python 3.9+ installed
- [ ] Node.js 18+ installed
- [ ] Ollama installed with llama3 model
- [ ] Supabase account created

## Step-by-Step Setup

### 1. Install Ollama & Model (2 minutes)

```bash
# Install Ollama from https://ollama.ai
# Then pull the model:
ollama pull llama3

# Verify:
ollama list
```

### 2. Set Up Supabase (3 minutes)

1. Go to https://supabase.com and create a project
2. Get your credentials (Settings → API):
   - Project URL
   - anon key
   - service_role key
3. Create `.env` in `religiousAI/`:
   ```env
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_ANON_KEY=your-anon-key
   SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
   ```
4. Apply schema:
   - Go to Supabase Dashboard → SQL Editor
   - Copy/paste `religiousAI/db_schema.sql`
   - Click Run

### 3. Backend Setup (2 minutes)

```bash
cd religiousAI

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download scriptures
python download_scriptures.py --all

# Build vector index
python build_index.py
```

### 4. Frontend Setup (1 minute)

```bash
cd divine-dialogue-main

# Install dependencies
npm install

# Create .env (optional)
echo "VITE_API_URL=http://localhost:8000" > .env
```

### 5. Run the Application (1 minute)

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

**Open:** http://localhost:8080

## Verify Everything Works

1. ✅ Backend running: http://localhost:8000/docs
2. ✅ Frontend running: http://localhost:8080
3. ✅ Sign up a new user
4. ✅ Send a chat message
5. ✅ Check Supabase dashboard - data should appear

## Next Steps

- Read [README.md](./README.md) for full documentation
- See [INTEGRATION.md](./INTEGRATION.md) for detailed setup
- See [SUPABASE_SETUP.md](./SUPABASE_SETUP.md) for database details

## Common Issues

**Backend won't start?**
- Check Ollama is running: `ollama list`
- Verify `.env` file exists with Supabase credentials

**Frontend can't connect?**
- Verify backend is running on port 8000
- Check `VITE_API_URL` in frontend `.env`

**Database errors?**
- Make sure you ran `db_schema.sql` in Supabase
- Check Supabase project is active (not paused)

---

That's it! You're ready to use Divine Wisdom Guide. 🎉

