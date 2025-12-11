-- Divine Wisdom Guide - Supabase Database Schema
-- Run this SQL in your Supabase SQL Editor to create all tables

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Enable pg_trgm for fuzzy text search
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- =====================================================================
-- USERS TABLE (extends Supabase auth.users)
-- =====================================================================
CREATE TABLE IF NOT EXISTS public.users (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT UNIQUE NOT NULL,
    name TEXT,
    preferences JSONB DEFAULT '{"default_religion": "christianity", "theme": "dark"}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_login TIMESTAMPTZ,
    visit_count INTEGER DEFAULT 0
);

-- Enable RLS on users table
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;

-- RLS Policy: Users can read their own data
CREATE POLICY "Users can view own profile"
    ON public.users FOR SELECT
    USING (auth.uid() = id);

-- RLS Policy: Users can update their own data
CREATE POLICY "Users can update own profile"
    ON public.users FOR UPDATE
    USING (auth.uid() = id);

-- =====================================================================
-- USER_MEMORY TABLE
-- =====================================================================
CREATE TABLE IF NOT EXISTS public.user_memory (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    themes TEXT[] DEFAULT '{}',
    personality_traits JSONB DEFAULT '{}'::jsonb,
    spiritual_journey JSONB DEFAULT '{"primary_concerns": [], "growth_areas": [], "milestones": []}'::jsonb,
    preferred_wisdom_style TEXT,
    conversation_summary TEXT,
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id)
);

-- Enable RLS on user_memory table
ALTER TABLE public.user_memory ENABLE ROW LEVEL SECURITY;

-- RLS Policy: Users can only access their own memory
CREATE POLICY "Users can manage own memory"
    ON public.user_memory
    FOR ALL
    USING (auth.uid() = user_id);

-- Index for faster lookups
CREATE INDEX IF NOT EXISTS idx_user_memory_user_id ON public.user_memory(user_id);

-- =====================================================================
-- CHATS TABLE
-- =====================================================================
CREATE TABLE IF NOT EXISTS public.chats (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    religion TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    is_current BOOLEAN DEFAULT FALSE
);

-- Enable RLS on chats table
ALTER TABLE public.chats ENABLE ROW LEVEL SECURITY;

-- RLS Policy: Users can only access their own chats
CREATE POLICY "Users can manage own chats"
    ON public.chats
    FOR ALL
    USING (auth.uid() = user_id);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_chats_user_id ON public.chats(user_id);
CREATE INDEX IF NOT EXISTS idx_chats_user_current ON public.chats(user_id, is_current) WHERE is_current = TRUE;
CREATE INDEX IF NOT EXISTS idx_chats_updated_at ON public.chats(updated_at DESC);

-- =====================================================================
-- CHAT_MESSAGES TABLE
-- =====================================================================
CREATE TABLE IF NOT EXISTS public.chat_messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    chat_id UUID NOT NULL REFERENCES public.chats(id) ON DELETE CASCADE,
    role TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    traditions TEXT[] DEFAULT '{}',
    sources JSONB DEFAULT '[]'::jsonb
);

-- Enable RLS on chat_messages table
ALTER TABLE public.chat_messages ENABLE ROW LEVEL SECURITY;

-- RLS Policy: Users can only access messages in their own chats
CREATE POLICY "Users can manage own chat messages"
    ON public.chat_messages
    FOR ALL
    USING (
        EXISTS (
            SELECT 1 FROM public.chats
            WHERE chats.id = chat_messages.chat_id
            AND chats.user_id = auth.uid()
        )
    );

-- Indexes
CREATE INDEX IF NOT EXISTS idx_chat_messages_chat_id ON public.chat_messages(chat_id);
CREATE INDEX IF NOT EXISTS idx_chat_messages_timestamp ON public.chat_messages(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_chat_messages_content_search ON public.chat_messages USING gin(to_tsvector('english', content));

-- =====================================================================
-- JOURNAL_ENTRIES TABLE
-- =====================================================================
CREATE TABLE IF NOT EXISTS public.journal_entries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    entry TEXT NOT NULL,
    reflection TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enable RLS on journal_entries table
ALTER TABLE public.journal_entries ENABLE ROW LEVEL SECURITY;

-- RLS Policy: Users can only access their own journal entries
CREATE POLICY "Users can manage own journal entries"
    ON public.journal_entries
    FOR ALL
    USING (auth.uid() = user_id);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_journal_entries_user_id ON public.journal_entries(user_id);
CREATE INDEX IF NOT EXISTS idx_journal_entries_created_at ON public.journal_entries(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_journal_entries_entry_search ON public.journal_entries USING gin(to_tsvector('english', entry));

-- =====================================================================
-- COMMUNITY_PROFILES TABLE
-- =====================================================================
CREATE TABLE IF NOT EXISTS public.community_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL UNIQUE REFERENCES public.users(id) ON DELETE CASCADE,
    display_name TEXT NOT NULL,
    bio TEXT,
    traits JSONB DEFAULT '{}'::jsonb,
    preferred_traditions TEXT[] DEFAULT '{}',
    opt_in BOOLEAN DEFAULT TRUE,
    last_active TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enable RLS on community_profiles table
ALTER TABLE public.community_profiles ENABLE ROW LEVEL SECURITY;

-- RLS Policy: Users can read all opted-in profiles, but only update their own
CREATE POLICY "Users can view opted-in profiles"
    ON public.community_profiles FOR SELECT
    USING (opt_in = TRUE OR auth.uid() = user_id);

CREATE POLICY "Users can manage own profile"
    ON public.community_profiles
    FOR ALL
    USING (auth.uid() = user_id);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_community_profiles_user_id ON public.community_profiles(user_id);
CREATE INDEX IF NOT EXISTS idx_community_profiles_opt_in ON public.community_profiles(opt_in) WHERE opt_in = TRUE;
CREATE INDEX IF NOT EXISTS idx_community_profiles_traits ON public.community_profiles USING gin(traits);
CREATE INDEX IF NOT EXISTS idx_community_profiles_traditions ON public.community_profiles USING gin(preferred_traditions);

-- =====================================================================
-- CONNECTION_REQUESTS TABLE
-- =====================================================================
CREATE TABLE IF NOT EXISTS public.connection_requests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    from_user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    to_user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    message TEXT DEFAULT '',
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'accepted', 'declined')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    responded_at TIMESTAMPTZ,
    UNIQUE(from_user_id, to_user_id)
);

-- Enable RLS on connection_requests table
ALTER TABLE public.connection_requests ENABLE ROW LEVEL SECURITY;

-- RLS Policy: Users can only see requests they sent or received
CREATE POLICY "Users can view own connection requests"
    ON public.connection_requests FOR SELECT
    USING (auth.uid() = from_user_id OR auth.uid() = to_user_id);

CREATE POLICY "Users can create connection requests"
    ON public.connection_requests FOR INSERT
    WITH CHECK (auth.uid() = from_user_id);

CREATE POLICY "Users can update received requests"
    ON public.connection_requests FOR UPDATE
    USING (auth.uid() = to_user_id);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_connection_requests_from_user ON public.connection_requests(from_user_id);
CREATE INDEX IF NOT EXISTS idx_connection_requests_to_user ON public.connection_requests(to_user_id);
CREATE INDEX IF NOT EXISTS idx_connection_requests_status ON public.connection_requests(status) WHERE status = 'pending';

-- =====================================================================
-- CONNECTIONS TABLE
-- =====================================================================
CREATE TABLE IF NOT EXISTS public.connections (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    connected_user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, connected_user_id),
    CHECK (user_id != connected_user_id)
);

-- Enable RLS on connections table
ALTER TABLE public.connections ENABLE ROW LEVEL SECURITY;

-- RLS Policy: Users can only see their own connections
CREATE POLICY "Users can view own connections"
    ON public.connections FOR SELECT
    USING (auth.uid() = user_id OR auth.uid() = connected_user_id);

CREATE POLICY "Users can create connections"
    ON public.connections FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_connections_user_id ON public.connections(user_id);
CREATE INDEX IF NOT EXISTS idx_connections_connected_user_id ON public.connections(connected_user_id);

-- =====================================================================
-- TRIGGERS FOR AUTO-UPDATES
-- =====================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply trigger to tables with updated_at
CREATE TRIGGER update_chats_updated_at
    BEFORE UPDATE ON public.chats
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_memory_updated_at
    BEFORE UPDATE ON public.user_memory
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_community_profiles_updated_at
    BEFORE UPDATE ON public.community_profiles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- =====================================================================
-- FUNCTION: Update chat updated_at when message is added
-- =====================================================================
CREATE OR REPLACE FUNCTION update_chat_on_message()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE public.chats
    SET updated_at = NOW()
    WHERE id = NEW.chat_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_chat_on_message_insert
    AFTER INSERT ON public.chat_messages
    FOR EACH ROW
    EXECUTE FUNCTION update_chat_on_message();

-- =====================================================================
-- FUNCTION: Handle connection request acceptance
-- =====================================================================
CREATE OR REPLACE FUNCTION handle_connection_acceptance()
RETURNS TRIGGER AS $$
BEGIN
    -- When a connection request is accepted, create bidirectional connections
    IF NEW.status = 'accepted' AND OLD.status = 'pending' THEN
        -- Insert connection from requester to recipient
        INSERT INTO public.connections (user_id, connected_user_id)
        VALUES (NEW.from_user_id, NEW.to_user_id)
        ON CONFLICT (user_id, connected_user_id) DO NOTHING;
        
        -- Insert connection from recipient to requester
        INSERT INTO public.connections (user_id, connected_user_id)
        VALUES (NEW.to_user_id, NEW.from_user_id)
        ON CONFLICT (user_id, connected_user_id) DO NOTHING;
        
        -- Update responded_at timestamp
        NEW.responded_at = NOW();
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER connection_acceptance_trigger
    BEFORE UPDATE ON public.connection_requests
    FOR EACH ROW
    EXECUTE FUNCTION handle_connection_acceptance();

-- =====================================================================
-- FUNCTION: Create user_memory record when user is created
-- =====================================================================
CREATE OR REPLACE FUNCTION create_user_memory()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.user_memory (user_id)
    VALUES (NEW.id)
    ON CONFLICT (user_id) DO NOTHING;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER create_user_memory_on_signup
    AFTER INSERT ON public.users
    FOR EACH ROW
    EXECUTE FUNCTION create_user_memory();

-- =====================================================================
-- VIEWS FOR COMMON QUERIES
-- =====================================================================

-- View for chat summaries (for sidebar)
CREATE OR REPLACE VIEW chat_summaries AS
SELECT 
    c.id,
    c.user_id,
    c.title,
    c.religion,
    c.created_at,
    c.updated_at,
    c.is_current,
    COUNT(cm.id) as message_count,
    (SELECT content FROM public.chat_messages 
     WHERE chat_id = c.id 
     ORDER BY timestamp DESC 
     LIMIT 1) as preview
FROM public.chats c
LEFT JOIN public.chat_messages cm ON c.id = cm.chat_id
GROUP BY c.id, c.user_id, c.title, c.religion, c.created_at, c.updated_at, c.is_current;

-- =====================================================================
-- GRANT PERMISSIONS
-- =====================================================================

-- Grant necessary permissions to authenticated users
GRANT USAGE ON SCHEMA public TO authenticated;
GRANT ALL ON ALL TABLES IN SCHEMA public TO authenticated;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO authenticated;

-- Grant permissions to anon role for public read operations (if needed)
-- GRANT SELECT ON public.community_profiles TO anon WHERE opt_in = TRUE;

