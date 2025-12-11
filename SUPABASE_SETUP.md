# Supabase Integration Guide

Complete guide for setting up and using Supabase as the database for Divine Wisdom Guide.

## 📋 Table of Contents

1. [What is Supabase?](#what-is-supabase)
2. [Initial Setup](#initial-setup)
3. [Database Schema](#database-schema)
4. [Configuration](#configuration)
5. [Data Migration](#data-migration)
6. [Features & Capabilities](#features--capabilities)
7. [Security](#security)
8. [Troubleshooting](#troubleshooting)

## 🔍 What is Supabase?

Supabase is an open-source Firebase alternative that provides:

- **PostgreSQL Database**: Full-featured relational database
- **Authentication**: Built-in user management
- **Real-time**: Live data subscriptions
- **Storage**: File storage for images, audio, etc.
- **Row Level Security**: Fine-grained access control

## 🚀 Initial Setup

### Step 1: Create Supabase Project

1. Go to https://supabase.com
2. Sign up or log in
3. Click "New Project"
4. Fill in:
   - **Name**: Your project name
   - **Database Password**: Choose a strong password
   - **Region**: Choose closest to your users
5. Click "Create new project"

Wait 2-3 minutes for the project to be created.

### Step 2: Get Your Credentials

1. Go to **Settings** → **API**
2. Copy these values:
   - **Project URL**: `https://xxxxx.supabase.co`
   - **anon public key**: Starts with `eyJhbGc...`
   - **service_role key**: Starts with `eyJhbGc...` (click "Reveal")

### Step 3: Configure Environment Variables

Create `.env` file in `religiousAI/`:

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key-here
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key-here
```

**Important:** 
- Never commit `.env` to git (already in `.gitignore`)
- `anon` key is safe for client-side use
- `service_role` key is secret - only use server-side

### Step 4: Install Dependencies

```bash
cd religiousAI
source venv/bin/activate
pip install supabase python-dotenv
```

### Step 5: Apply Database Schema

1. Go to Supabase Dashboard → **SQL Editor**
2. Click **New Query**
3. Open `religiousAI/db_schema.sql`
4. Copy the entire file contents
5. Paste into SQL Editor
6. Click **Run** (or press Cmd/Ctrl + Enter)

This creates:
- All database tables
- Indexes for performance
- Row Level Security policies
- Database functions and triggers

**Verify:** Go to **Table Editor** - you should see all tables listed.

## 📊 Database Schema

### Tables Overview

| Table | Purpose |
|-------|---------|
| `users` | User profiles (extends auth.users) |
| `user_memory` | Themes, personality, spiritual journey |
| `chats` | Chat conversation threads |
| `chat_messages` | Individual messages in chats |
| `journal_entries` | Journal entries and reflections |
| `community_profiles` | Community matching profiles |
| `connection_requests` | Connection requests between users |
| `connections` | Established connections |

### Key Relationships

```
auth.users (Supabase Auth)
    ↓
users (public.users)
    ↓
├── user_memory (1:1)
├── chats (1:many)
│   └── chat_messages (1:many)
├── journal_entries (1:many)
└── community_profiles (1:1)
    ├── connection_requests (many:many)
    └── connections (many:many)
```

### Row Level Security (RLS)

All tables have RLS enabled with policies:

- **Users can only access their own data**
- **Community profiles are readable by all (if opted-in)**
- **Connection requests only visible to involved users**
- **Chat messages only accessible by chat owner**

## ⚙️ Configuration

### Enable/Disable Supabase

In `config.py`:

```python
USE_SUPABASE = True  # Use Supabase (recommended)
# USE_SUPABASE = False  # Fall back to file-based storage
```

When `USE_SUPABASE = False`, the app falls back to JSON file storage (for development/testing).

### Verify Connection

Test your connection:

```bash
cd religiousAI
source venv/bin/activate
python -c "from supabase_client import initialize_clients; initialize_clients(); print('✓ Connected!')"
```

## 📦 Data Migration

### Migrating Existing JSON Data

If you have existing user data in JSON files:

```bash
cd religiousAI
source venv/bin/activate
python migrate_data.py
```

**What gets migrated:**
- ✅ User accounts → Supabase Auth + public.users
- ✅ User memory (themes, personality) → user_memory table
- ✅ Conversations → chats + chat_messages tables
- ✅ Journal entries → journal_entries table
- ✅ Community profiles → community_profiles table
- ✅ Connections → connections table

**What doesn't get migrated:**
- ❌ Session files (Supabase handles sessions)
- ❌ Password hashes (users reset passwords)

**After Migration:**
1. Users will have temporary passwords
2. They need to use "Forgot Password" to reset
3. Verify data in Supabase dashboard
4. Test login and functionality

### Cleaning Up JSON Files

**After verifying migration is successful:**

```bash
cd religiousAI
source venv/bin/activate
python cleanup_json_files.py
```

The script will:
- Show what files will be deleted
- Offer to create backups
- Require explicit confirmation ("DELETE")

## ✨ Features & Capabilities

### 1. Real-time Subscriptions

Get live updates for community features:

```python
from supabase_realtime import subscribe_to_connection_requests

def handle_new_request(data):
    print(f"New connection request: {data}")

subscription = subscribe_to_connection_requests(user_id, handle_new_request)
```

### 2. Full-Text Search

Search through chats and journal entries:

```python
from search import search_chat_messages, search_journal_entries

# Search chats
results = search_chat_messages(user_id, "peace", limit=10)

# Search journal entries
results = search_journal_entries(user_id, "gratitude", limit=10)
```

### 3. Storage (Optional)

Store audio files and images:

1. Go to Supabase Dashboard → **Storage**
2. Create buckets:
   - `audio` (private) - TTS audio files
   - `profile-images` (public) - User profile pictures
   - `scripture-audio` (public) - Pre-generated audio

### 4. Database Functions

Automatic features via triggers:

- **Auto-update timestamps**: `updated_at` fields update automatically
- **Connection creation**: When request accepted, connections created automatically
- **User memory creation**: Created automatically when user signs up

### 5. Views

Pre-built views for common queries:

- `chat_summaries` - Quick chat list with message counts and previews

## 🔒 Security

### Row Level Security (RLS)

All tables have RLS policies that ensure:

1. **Data Isolation**: Users can only see their own data
2. **Community Privacy**: Profiles only visible if opted-in
3. **Connection Privacy**: Requests only visible to involved users

### API Keys

- **Anon Key**: Safe for client-side use (enforces RLS)
- **Service Role Key**: Secret - only use server-side (bypasses RLS)

### Best Practices

1. ✅ Never commit `.env` file
2. ✅ Use anon key in frontend
3. ✅ Use service_role key only in backend
4. ✅ Keep service_role key secret
5. ✅ Review RLS policies regularly

## 🐛 Troubleshooting

### "Table does not exist"

**Solution:**
- Make sure you ran `db_schema.sql` in Supabase SQL Editor
- Check table names are correct (case-sensitive)
- Verify you're connected to the right project

### "RLS policy violation"

**Solution:**
- Verify user is authenticated
- Check RLS policies in Supabase dashboard
- Ensure `user_id` matches `auth.uid()`
- Try using service_role key for testing (server-side only)

### "Connection failed"

**Solution:**
- Check `.env` file has correct credentials
- Verify Supabase project is active (not paused)
- Check network connectivity
- Verify project URL format: `https://xxxxx.supabase.co`

### "User not found" after migration

**Solution:**
- Users need to reset passwords after migration
- Use "Forgot Password" in the app
- Or manually reset in Supabase Dashboard → Authentication

### Data not appearing

**Solution:**
- Check Supabase Table Editor to see if data exists
- Verify RLS policies allow reads
- Check browser console for errors
- Verify user is authenticated

### Migration script errors

**Solution:**
- Make sure schema is applied first
- Check service_role key is correct
- Verify JSON files exist and are valid
- Check script output for specific errors

## 📚 Additional Resources

- [Supabase Documentation](https://supabase.com/docs)
- [Supabase Python Client](https://supabase.com/docs/reference/python/introduction)
- [Row Level Security Guide](https://supabase.com/docs/guides/auth/row-level-security)
- [Supabase Auth](https://supabase.com/docs/guides/auth)
- [Supabase Realtime](https://supabase.com/docs/guides/realtime)

## 🎯 Quick Reference

### Common Tasks

**View data:**
- Supabase Dashboard → Table Editor

**Run SQL:**
- Supabase Dashboard → SQL Editor

**Check auth users:**
- Supabase Dashboard → Authentication → Users

**View logs:**
- Supabase Dashboard → Logs

**Manage storage:**
- Supabase Dashboard → Storage

### Useful SQL Queries

**Count users:**
```sql
SELECT COUNT(*) FROM auth.users;
```

**View all chats for a user:**
```sql
SELECT * FROM chats WHERE user_id = 'user-uuid-here';
```

**Check RLS policies:**
```sql
SELECT * FROM pg_policies WHERE tablename = 'chats';
```

---

For integration with React frontend, see [INTEGRATION.md](./INTEGRATION.md).
