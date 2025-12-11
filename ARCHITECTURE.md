# Architecture Documentation

Complete overview of how the Divine Wisdom Guide application is structured and how components interact.

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         User's Browser                          │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              React Frontend (Port 8080)                  │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │  │
│  │  │   Chat UI    │  │  Community   │  │    Auth      │  │  │
│  │  └──────────────┘  └──────────────┘  └──────────────┘  │  │
│  │                                                          │  │
│  │  API Client (src/lib/api.ts)                            │  │
│  └──────────────────────┬───────────────────────────────────┘  │
└─────────────────────────┼───────────────────────────────────────┘
                          │ HTTP/REST API
                          │ (JSON)
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│              FastAPI Backend (Port 8000)                        │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    API Layer (api.py)                    │  │
│  │  - Request validation                                    │  │
│  │  - Authentication                                        │  │
│  │  - Response formatting                                   │  │
│  └──────┬───────────────┬───────────────┬───────────────────┘  │
│         │               │               │                      │
│         ▼               ▼               ▼                      │
│  ┌──────────┐   ┌──────────┐   ┌──────────────┐              │
│  │  Auth    │   │  Memory  │   │  Community   │              │
│  │ (auth.py)│   │(memory.py)│  │(community.py)│              │
│  └────┬─────┘   └────┬─────┘   └──────┬───────┘              │
│       │              │                 │                      │
│       ▼              ▼                 ▼                      │
│  ┌──────────────────────────────────────────────┐            │
│  │         Supabase Client                      │            │
│  │    (supabase_client.py)                      │            │
│  └──────────────────┬───────────────────────────┘            │
│                     │                                         │
│         ┌───────────┴───────────┐                            │
│         ▼                       ▼                            │
│  ┌──────────────┐      ┌──────────────┐                     │
│  │   Ollama     │      │   Supabase   │                     │
│  │   (llama3)   │      │  PostgreSQL  │                     │
│  └──────────────┘      └──────────────┘                     │
│         │                       │                            │
│         └───────────┬───────────┘                            │
│                     ▼                                        │
│            ┌──────────────┐                                  │
│            │   ChromaDB   │                                  │
│            │ Vector Store │                                  │
│            └──────────────┘                                  │
└───────────────────────────────────────────────────────────────┘
```

## 📦 Component Overview

### Frontend (React/TypeScript)

**Location:** `divine-dialogue-main/`

**Key Components:**
- `src/pages/Chat.tsx` - Main chat interface
- `src/pages/Community.tsx` - Community features
- `src/pages/Login.tsx` - Authentication
- `src/lib/api.ts` - API client (all backend communication)

**Responsibilities:**
- User interface and interactions
- API calls to backend
- Local state management
- Authentication UI
- Real-time UI updates

### Backend (FastAPI/Python)

**Location:** `religiousAI/`

**Key Modules:**

#### API Layer (`api.py`)
- REST API endpoints
- Request/response handling
- CORS configuration
- Error handling

#### Authentication (`auth.py`)
- User signup/login
- Session management
- Uses Supabase Auth
- Token validation

#### Memory Management (`memory.py`)
- User memory storage
- Chat thread management
- Theme extraction
- Personality insights
- Uses Supabase database

#### Community (`community.py`)
- Profile management
- User matching
- Connection requests
- Uses Supabase database

#### AI Logic (`qa.py`)
- Question answering
- Scripture retrieval
- Meditation generation
- Comparison logic
- Uses Ollama LLM + ChromaDB

#### Safety (`safety.py`)
- Crisis detection
- Content filtering
- Safety guardrails

### Database (Supabase PostgreSQL)

**Tables:**
- `users` - User profiles
- `user_memory` - Themes, personality, spiritual journey
- `chats` - Conversation threads
- `chat_messages` - Individual messages
- `journal_entries` - Journal entries
- `community_profiles` - Community profiles
- `connection_requests` - Connection requests
- `connections` - Established connections

**Features:**
- Row Level Security (RLS)
- Real-time subscriptions
- Full-text search
- Automatic triggers

### Vector Store (ChromaDB)

**Purpose:**
- Stores scripture embeddings
- Enables semantic search
- Retrieves relevant passages for AI responses

**Location:** `vectorstore/`

## 🔄 Data Flow Examples

### Example 1: User Sends a Chat Message

```
1. User types message in React UI
   ↓
2. Frontend calls POST /api/chat
   ↓
3. Backend (api.py) receives request
   ↓
4. Backend validates authentication
   ↓
5. Backend queries ChromaDB for relevant scriptures
   ↓
6. Backend calls Ollama LLM with context
   ↓
7. LLM generates response
   ↓
8. Backend saves message to Supabase (chats, chat_messages)
   ↓
9. Backend updates user memory (themes, personality)
   ↓
10. Backend returns response to frontend
   ↓
11. Frontend displays response in chat UI
```

### Example 2: User Signs Up

```
1. User fills signup form in React UI
   ↓
2. Frontend calls POST /api/auth/signup
   ↓
3. Backend (auth.py) creates user in Supabase Auth
   ↓
4. Supabase Auth creates auth.users record
   ↓
5. Database trigger creates public.users record
   ↓
6. Database trigger creates user_memory record
   ↓
7. Backend returns auth token
   ↓
8. Frontend stores token in localStorage
   ↓
9. User is logged in
```

### Example 3: Community Matching

```
1. User creates community profile
   ↓
2. Backend saves profile to Supabase
   ↓
3. User requests matches
   ↓
4. Backend queries all opted-in profiles
   ↓
5. Backend calculates compatibility scores
   ↓
6. Backend returns sorted matches
   ↓
7. Frontend displays matches
```

## 🔐 Security Architecture

### Authentication Flow

1. User signs up/logs in → Supabase Auth
2. Supabase returns JWT token
3. Token stored in localStorage (frontend)
4. Token sent in Authorization header (API requests)
5. Backend validates token with Supabase
6. Backend uses `auth.uid()` for RLS

### Row Level Security (RLS)

Every table has RLS policies:

```sql
-- Example: Users can only see their own chats
CREATE POLICY "Users can manage own chats"
    ON public.chats
    FOR ALL
    USING (auth.uid() = user_id);
```

This ensures:
- Users can only access their own data
- No data leakage between users
- Automatic security at database level

## 📊 Database Schema Relationships

```
auth.users (Supabase Auth)
    │
    ├── id (UUID)
    │
    ▼
public.users
    │
    ├── id (references auth.users.id)
    ├── email
    ├── name
    └── preferences
    │
    ├──► user_memory (1:1)
    │   ├── themes
    │   ├── personality_traits
    │   └── spiritual_journey
    │
    ├──► chats (1:many)
    │   └──► chat_messages (1:many)
    │       ├── role (user/assistant)
    │       ├── content
    │       └── traditions
    │
    ├──► journal_entries (1:many)
    │   ├── entry
    │   └── reflection
    │
    └──► community_profiles (1:1)
        ├── display_name
        ├── traits
        ├──► connection_requests (many:many)
        └──► connections (many:many)
```

## 🔄 State Management

### Frontend State

- **Local State**: React useState/useReducer
- **API State**: Fetched on demand, cached in component state
- **Auth State**: Token in localStorage, user data in state

### Backend State

- **Database**: All persistent data in Supabase
- **Session**: Managed by Supabase Auth
- **Memory**: User memory in Supabase (not in-memory)

### Vector Store

- **Embeddings**: Stored in ChromaDB
- **Scriptures**: Text files in `data/raw/`
- **Index**: Built once, used for all queries

## 🚀 Deployment Architecture

### Development

```
Frontend (localhost:8080) → Backend (localhost:8000) → Supabase (cloud)
```

### Production

```
Frontend (CDN/Static Host) → Backend (Server/Container) → Supabase (cloud)
                              ↓
                         Ollama (Server)
                              ↓
                         ChromaDB (Server)
```

## 📈 Scalability Considerations

### Current Setup (Suitable for small-medium scale)

- **Supabase**: Handles database scaling automatically
- **Ollama**: Single instance (can scale horizontally)
- **ChromaDB**: File-based (can migrate to server mode)

### Future Scaling Options

1. **Database**: Supabase scales automatically
2. **LLM**: Deploy multiple Ollama instances behind load balancer
3. **Vector Store**: Migrate ChromaDB to server mode or use Supabase pgvector
4. **Backend**: Deploy multiple FastAPI instances
5. **Frontend**: Static files on CDN

## 🔍 Key Design Decisions

### Why Supabase?

- **Built-in Auth**: No need to build authentication
- **PostgreSQL**: Full-featured relational database
- **RLS**: Security at database level
- **Real-time**: Built-in subscriptions
- **Free Tier**: Good for development

### Why FastAPI?

- **Fast**: High performance
- **Type Safety**: Pydantic models
- **Auto Docs**: Swagger/ReDoc
- **Async**: Supports async operations
- **Python**: Easy integration with AI libraries

### Why React?

- **Component-based**: Reusable UI components
- **TypeScript**: Type safety
- **Ecosystem**: Rich library ecosystem
- **Performance**: Fast rendering

### Why Ollama?

- **Local**: Run LLM locally (privacy)
- **Free**: No API costs
- **Flexible**: Easy to switch models
- **Offline**: Works without internet (for LLM)

## 🧪 Testing Strategy

### Unit Tests
- Test individual functions
- Mock external dependencies

### Integration Tests
- Test API endpoints
- Test database operations
- Test authentication flow

### End-to-End Tests
- Test full user flows
- Test UI interactions

## 📝 Code Organization

### Backend Structure

```
religiousAI/
├── api.py              # API endpoints (entry point)
├── auth.py             # Authentication logic
├── memory.py           # Memory management
├── community.py        # Community features
├── qa.py               # AI/LLM logic
├── safety.py           # Safety features
├── config.py           # Configuration
└── supabase_client.py  # Database client
```

### Frontend Structure

```
divine-dialogue-main/src/
├── pages/              # Page components
├── components/         # Reusable components
│   ├── chat/          # Chat-specific
│   └── ui/            # Generic UI
├── lib/                # Utilities
│   ├── api.ts         # API client
│   └── utils.ts       # Helpers
└── hooks/              # Custom hooks
```

## 🔄 Development Workflow

1. **Make changes** to code
2. **Backend auto-reloads** (uvicorn --reload)
3. **Frontend auto-reloads** (Vite HMR)
4. **Test in browser**
5. **Check Supabase dashboard** for data
6. **Commit changes**

## 📚 Further Reading

- [README.md](./README.md) - Main project documentation
- [INTEGRATION.md](./INTEGRATION.md) - Setup guide
- [SUPABASE_SETUP.md](./SUPABASE_SETUP.md) - Database setup
- [QUICKSTART.md](./QUICKSTART.md) - Quick start guide

