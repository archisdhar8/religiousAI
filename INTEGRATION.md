# Integration Guide: React Frontend + Python Backend

This guide explains how to run the integrated application with the React frontend and FastAPI backend.

## Architecture

- **Frontend**: React app in `divine-dialogue-main/` (runs on port 8080)
- **Backend**: FastAPI server in `religiousAI/` (runs on port 8000)
- **Communication**: REST API with CORS enabled

## Prerequisites

1. **Python 3.9+** with virtual environment
2. **Node.js 18+** and npm
3. **Ollama** with llama3 model installed:
   ```bash
   ollama pull llama3
   ```

## Setup Instructions

### 1. Backend Setup

```bash
cd religiousAI

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download scriptures and build vector index (if not done already)
python download_scriptures.py --all
python build_index.py
```

### 2. Frontend Setup

```bash
cd divine-dialogue-main

# Install dependencies
npm install

# Create .env file (optional, defaults to http://localhost:8000)
echo "VITE_API_URL=http://localhost:8000" > .env
```

### 3. Running the Application

You need to run both servers simultaneously:

#### Terminal 1 - Backend API Server

```bash
cd religiousAI
source venv/bin/activate  # Windows: venv\Scripts\activate
uvicorn api:app --reload --port 8000
```

The API will be available at: `http://localhost:8000`

#### Terminal 2 - Frontend Development Server

```bash
cd divine-dialogue-main
npm run dev
```

The frontend will be available at: `http://localhost:8080`

## API Endpoints

The FastAPI server exposes the following endpoints:

- `GET /` - Health check
- `GET /api/traditions` - Get available traditions
- `POST /api/chat` - Send a chat message and get response
- `GET /api/daily-wisdom` - Get daily wisdom quote
- `POST /api/compare` - Compare traditions on a topic
- `POST /api/journal` - Submit journal entry for reflection
- `GET /api/greeting` - Get personalized greeting
- `GET /api/user/{user_id}` - Get user memory summary

## API Documentation

Once the backend is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Environment Variables

### Frontend (.env)

```env
VITE_API_URL=http://localhost:8000
```

### Backend

No environment variables required. Configuration is in `config.py`.

## Troubleshooting

### CORS Errors

If you see CORS errors, ensure:
1. Backend is running on port 8000
2. Frontend is running on port 8080
3. CORS middleware in `api.py` allows `http://localhost:8080`

### Connection Refused

- Verify backend is running: `curl http://localhost:8000/`
- Check that Ollama is running: `ollama list`
- Ensure vectorstore is built: Check `vectorstore/` directory exists

### Frontend Can't Connect

- Verify `VITE_API_URL` in `.env` matches backend URL
- Check browser console for specific error messages
- Ensure no firewall is blocking port 8000

## Development Tips

1. **Hot Reload**: Both servers support hot reload during development
2. **Session Management**: Frontend stores session ID in localStorage
3. **User Memory**: Backend stores user data in `religiousAI/data/users/`
4. **Vector Store**: Scripture embeddings in `religiousAI/vectorstore/`

## Production Deployment

For production:

1. **Backend**: Use a production ASGI server like Gunicorn with Uvicorn workers
2. **Frontend**: Build static files with `npm run build` and serve with a web server
3. **CORS**: Update allowed origins in `api.py` to match your production domain
4. **Environment**: Set `VITE_API_URL` to your production API URL

## Notes

- The Streamlit app (`app.py`) is kept for reference but not used by the React frontend
- Session IDs are generated client-side and stored in localStorage
- User memory persists across sessions using the session ID

