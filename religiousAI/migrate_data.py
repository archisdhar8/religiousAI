"""
Enhanced Data Migration Script: File-based JSON to Supabase

This script migrates existing user data from JSON files to Supabase database.
It creates users in Supabase Auth and migrates all their data.

Usage:
    python migrate_data.py
"""

import os
import json
import hashlib
import httpx
from datetime import datetime
from typing import Dict, List, Optional
from supabase_client import get_supabase_client
from config import BASE_DIR, USE_SUPABASE

# Directories
USERS_DIR = os.path.join(BASE_DIR, "data", "users")
ACCOUNTS_DIR = os.path.join(BASE_DIR, "data", "accounts")
COMMUNITY_DIR = os.path.join(BASE_DIR, "data", "community")
PROFILES_DIR = os.path.join(COMMUNITY_DIR, "profiles")


def get_email_from_account_file(filepath: str) -> Optional[str]:
    """Extract email from account file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            account_data = json.load(f)
        return account_data.get("email", "").lower().strip()
    except:
        return None


def create_user_in_supabase(email: str, password: str, name: str) -> Optional[str]:
    """
    Create a user in Supabase Auth using Admin REST API.
    Returns user_id if successful, None otherwise.
    """
    try:
        import os
        from dotenv import load_dotenv
        load_dotenv()
        
        supabase_url = os.getenv("SUPABASE_URL")
        service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        
        if not supabase_url or not service_key:
            raise Exception("SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY not found in environment")
        
        # Use REST API directly with service role key
        response = httpx.post(
            f"{supabase_url}/auth/v1/admin/users",
            headers={
                "apikey": service_key,
                "Authorization": f"Bearer {service_key}",
                "Content-Type": "application/json"
            },
            json={
                "email": email,
                "password": password,
                "email_confirm": True,
                "user_metadata": {
                    "name": name
                }
            },
            timeout=30.0
        )
        
        if response.status_code == 200:
            user_data = response.json()
            user_id = user_data.get("id")
            
            if not user_id:
                raise Exception("User ID not found in response")
            
            # Create user profile in public.users
            supabase = get_supabase_client(use_service_role=True)
            supabase.table("users").insert({
                "id": user_id,
                "email": email,
                "name": name,
                "preferences": {
                    "default_religion": "christianity",
                    "theme": "dark"
                },
                "created_at": datetime.now().isoformat(),
                "visit_count": 0
            }).execute()
            
            return user_id
        else:
            error_text = response.text
            if response.status_code == 422 and "already registered" in error_text.lower():
                # User already exists, try to get their ID
                supabase = get_supabase_client(use_service_role=True)
                user_response = supabase.table("users").select("id").eq("email", email).execute()
                if user_response.data:
                    return user_response.data[0]["id"]
            raise Exception(f"API error: {response.status_code} - {error_text}")
        
    except Exception as e:
        print(f"    Error creating user in Supabase: {e}")
        return None


def migrate_user_accounts():
    """Migrate user accounts from files to Supabase Auth."""
    if not USE_SUPABASE:
        print("Supabase is disabled. Set USE_SUPABASE=True in config.py")
        return {}
    
    if not os.path.exists(ACCOUNTS_DIR):
        print(f"Accounts directory not found: {ACCOUNTS_DIR}")
        return {}
    
    supabase = get_supabase_client(use_service_role=True)
    
    migrated = {}
    skipped = 0
    errors = 0
    
    print("\n" + "=" * 60)
    print("STEP 1: Migrating User Accounts")
    print("=" * 60)
    
    for filename in os.listdir(ACCOUNTS_DIR):
        if not filename.endswith('.json'):
            continue
        
        filepath = os.path.join(ACCOUNTS_DIR, filename)
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                user_data = json.load(f)
            
            email = user_data.get("email", "").lower().strip()
            if not email:
                print(f"  ⚠️  Skipping {filename}: No email found")
                skipped += 1
                continue
            
            # Check if user already exists
            existing = supabase.table("users").select("id, email").eq("email", email).execute()
            if existing.data:
                print(f"  ✓ User {email} already exists in Supabase")
                migrated[email] = existing.data[0]["id"]
                continue
            
            # Get user info
            name = user_data.get("name", email.split("@")[0])
            password_hash = user_data.get("password_hash", "")
            
            # Generate a temporary password (users will need to reset)
            # We can't decrypt the old password hash, so we'll set a temp password
            temp_password = f"TempPass{hashlib.md5(email.encode()).hexdigest()[:8]}!"
            
            print(f"  → Creating user: {email} ({name})")
            user_id = create_user_in_supabase(email, temp_password, name)
            
            if user_id:
                print(f"    ✓ Created user with ID: {user_id}")
                print(f"    ⚠️  Temporary password set. User should reset password on first login.")
                migrated[email] = user_id
            else:
                print(f"    ✗ Failed to create user")
                errors += 1
                
        except Exception as e:
            print(f"  ✗ Error processing {filename}: {e}")
            errors += 1
    
    print(f"\n  Summary: {len(migrated)} migrated, {skipped} skipped, {errors} errors")
    return migrated


def migrate_user_memory(email_to_user_id: Dict[str, str]):
    """Migrate user memory/conversations to Supabase."""
    if not USE_SUPABASE:
        return
    
    if not os.path.exists(USERS_DIR):
        print(f"\nUsers directory not found: {USERS_DIR}")
        return
    
    supabase = get_supabase_client(use_service_role=True)
    
    migrated = 0
    skipped = 0
    errors = 0
    
    print("\n" + "=" * 60)
    print("STEP 2: Migrating User Memory & Conversations")
    print("=" * 60)
    
    for filename in os.listdir(USERS_DIR):
        if not filename.endswith('.json'):
            continue
        
        filepath = os.path.join(USERS_DIR, filename)
        user_id_hash = filename.replace('.json', '')
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                memory_data = json.load(f)
            
            email = memory_data.get("email", "").lower().strip()
            if not email:
                # Try to match by hash - find account file with matching hash
                print(f"  ⚠️  No email in {filename}, trying to match by hash...")
                skipped += 1
                continue
            
            # Get user_id from migrated accounts
            user_id = email_to_user_id.get(email)
            if not user_id:
                print(f"  ⚠️  User {email} not found in migrated accounts, skipping memory...")
                skipped += 1
                continue
            
            print(f"  → Migrating memory for: {email}")
            
            # Migrate user_memory
            memory_record = {
                "user_id": user_id,
                "themes": memory_data.get("themes", []),
                "personality_traits": memory_data.get("personality_traits", {}),
                "spiritual_journey": memory_data.get("spiritual_journey", {
                    "primary_concerns": [],
                    "growth_areas": [],
                    "milestones": []
                }),
                "preferred_wisdom_style": memory_data.get("preferred_wisdom_style"),
                "conversation_summary": memory_data.get("conversation_summary", ""),
                "updated_at": memory_data.get("last_visit", datetime.now().isoformat())
            }
            
            supabase.table("user_memory").upsert(memory_record, on_conflict="user_id").execute()
            print(f"    ✓ Migrated user memory")
            
            # Migrate chats from old conversations format
            old_conversations = memory_data.get("conversations", [])
            chats_created = 0
            messages_created = 0
            
            for conv in old_conversations:
                exchanges = conv.get("exchanges", [])
                if not exchanges:
                    continue
                
                # Create chat
                title = exchanges[0].get("question", "Conversation")[:40]
                if len(exchanges[0].get("question", "")) > 40:
                    title += "..."
                
                chat_data = {
                    "user_id": user_id,
                    "title": title,
                    "religion": exchanges[0].get("traditions", [None])[0] if exchanges[0].get("traditions") else None,
                    "created_at": conv.get("date", datetime.now().isoformat()),
                    "updated_at": conv.get("date", datetime.now().isoformat()),
                    "is_current": False
                }
                
                chat_response = supabase.table("chats").insert(chat_data).execute()
                if not chat_response.data:
                    continue
                
                chat_id = chat_response.data[0]["id"]
                chats_created += 1
                
                # Add messages
                for exchange in exchanges:
                    # User message
                    supabase.table("chat_messages").insert({
                        "chat_id": chat_id,
                        "role": "user",
                        "content": exchange.get("question", ""),
                        "timestamp": exchange.get("timestamp", conv.get("date")),
                        "traditions": exchange.get("traditions", [])
                    }).execute()
                    messages_created += 1
                    
                    # Assistant message
                    supabase.table("chat_messages").insert({
                        "chat_id": chat_id,
                        "role": "assistant",
                        "content": exchange.get("answer", "")[:500],
                        "timestamp": exchange.get("timestamp", conv.get("date")),
                        "traditions": exchange.get("traditions", [])
                    }).execute()
                    messages_created += 1
            
            # Migrate journal entries
            journal_entries = memory_data.get("journal_entries", [])
            for entry in journal_entries:
                supabase.table("journal_entries").insert({
                    "user_id": user_id,
                    "entry": entry.get("entry", "")[:1000],
                    "reflection": entry.get("reflection", "")[:500],
                    "created_at": entry.get("date", datetime.now().isoformat())
                }).execute()
            
            print(f"    ✓ Created {chats_created} chats with {messages_created} messages")
            print(f"    ✓ Migrated {len(journal_entries)} journal entries")
            migrated += 1
            
        except Exception as e:
            print(f"  ✗ Error processing {filename}: {e}")
            import traceback
            traceback.print_exc()
            errors += 1
    
    print(f"\n  Summary: {migrated} migrated, {skipped} skipped, {errors} errors")


def migrate_community_profiles(email_to_user_id: Dict[str, str]):
    """Migrate community profiles to Supabase."""
    if not USE_SUPABASE:
        return
    
    if not os.path.exists(PROFILES_DIR):
        print(f"\nProfiles directory not found: {PROFILES_DIR}")
        return
    
    supabase = get_supabase_client(use_service_role=True)
    
    migrated = 0
    skipped = 0
    errors = 0
    
    print("\n" + "=" * 60)
    print("STEP 3: Migrating Community Profiles")
    print("=" * 60)
    
    for filename in os.listdir(PROFILES_DIR):
        if not filename.endswith('.json'):
            continue
        
        filepath = os.path.join(PROFILES_DIR, filename)
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                profile_data = json.load(f)
            
            email = profile_data.get("email", "").lower().strip()
            if not email:
                skipped += 1
                continue
            
            # Get user_id
            user_id = email_to_user_id.get(email)
            if not user_id:
                print(f"  ⚠️  User {email} not found, skipping profile...")
                skipped += 1
                continue
            
            # Check if profile already exists
            existing = supabase.table("community_profiles").select("id").eq("user_id", user_id).execute()
            if existing.data:
                print(f"  ✓ Profile for {email} already exists, skipping...")
                skipped += 1
                continue
            
            print(f"  → Migrating profile for: {email}")
            
            # Create profile
            profile_record = {
                "user_id": user_id,
                "display_name": profile_data.get("display_name", ""),
                "bio": profile_data.get("bio"),
                "traits": profile_data.get("traits", {}),
                "preferred_traditions": profile_data.get("preferred_traditions", []),
                "opt_in": profile_data.get("opt_in", True),
                "last_active": profile_data.get("last_active", datetime.now().isoformat()),
                "created_at": profile_data.get("created_at", datetime.now().isoformat()),
                "updated_at": profile_data.get("updated_at", datetime.now().isoformat())
            }
            
            supabase.table("community_profiles").insert(profile_record).execute()
            
            # Migrate connections (will be handled separately if both users exist)
            connections = profile_data.get("connections", [])
            connections_created = 0
            for conn_email in connections:
                conn_user_id = email_to_user_id.get(conn_email.lower())
                if conn_user_id:
                    try:
                        supabase.table("connections").insert({
                            "user_id": user_id,
                            "connected_user_id": conn_user_id
                        }).execute()
                        supabase.table("connections").insert({
                            "user_id": conn_user_id,
                            "connected_user_id": user_id
                        }).execute()
                        connections_created += 1
                    except:
                        pass
            
            print(f"    ✓ Created profile with {connections_created} connections")
            migrated += 1
            
        except Exception as e:
            print(f"  ✗ Error processing {filename}: {e}")
            errors += 1
    
    print(f"\n  Summary: {migrated} migrated, {skipped} skipped, {errors} errors")


def verify_migration(email_to_user_id: Dict[str, str]):
    """Verify that data was migrated correctly."""
    if not USE_SUPABASE:
        return
    
    supabase = get_supabase_client(use_service_role=True)
    
    print("\n" + "=" * 60)
    print("STEP 4: Verifying Migration")
    print("=" * 60)
    
    all_good = True
    
    for email, user_id in email_to_user_id.items():
        print(f"\n  Verifying: {email}")
        
        # Check user exists
        user_check = supabase.table("users").select("id, email, name").eq("id", user_id).execute()
        if not user_check.data:
            print(f"    ✗ User not found in Supabase")
            all_good = False
            continue
        print(f"    ✓ User exists: {user_check.data[0].get('name')}")
        
        # Check user_memory
        memory_check = supabase.table("user_memory").select("themes").eq("user_id", user_id).execute()
        if memory_check.data:
            themes = memory_check.data[0].get("themes", [])
            print(f"    ✓ User memory exists ({len(themes)} themes)")
        else:
            print(f"    ⚠️  No user memory found")
        
        # Check chats
        chats_check = supabase.table("chats").select("id").eq("user_id", user_id).execute()
        chat_count = len(chats_check.data) if chats_check.data else 0
        if chat_count > 0:
            # Count messages
            chat_ids = [c["id"] for c in chats_check.data]
            messages_check = supabase.table("chat_messages").select("id").in_("chat_id", chat_ids).execute()
            msg_count = len(messages_check.data) if messages_check.data else 0
            print(f"    ✓ {chat_count} chats with {msg_count} messages")
        else:
            print(f"    ⚠️  No chats found")
        
        # Check journal entries
        journal_check = supabase.table("journal_entries").select("id").eq("user_id", user_id).execute()
        journal_count = len(journal_check.data) if journal_check.data else 0
        if journal_count > 0:
            print(f"    ✓ {journal_count} journal entries")
        
        # Check community profile
        profile_check = supabase.table("community_profiles").select("id").eq("user_id", user_id).execute()
        if profile_check.data:
            print(f"    ✓ Community profile exists")
    
    if all_good:
        print("\n  ✓ All verifications passed!")
    else:
        print("\n  ⚠️  Some verifications failed. Please review above.")
    
    return all_good


def main():
    """Run all migrations."""
    print("=" * 60)
    print("Supabase Data Migration Script")
    print("=" * 60)
    print("\nThis script will:")
    print("1. Create users in Supabase Auth")
    print("2. Migrate user memory and conversations")
    print("3. Migrate community profiles")
    print("4. Verify the migration")
    print("\nWARNING: Users will need to reset their passwords!")
    print("Temporary passwords will be set during migration.")
    print()
    
    response = input("Continue with migration? (yes/no): ")
    if response.lower() != "yes":
        print("Migration cancelled.")
        return
    
    if not USE_SUPABASE:
        print("\nERROR: USE_SUPABASE is False in config.py")
        print("Set USE_SUPABASE=True to enable Supabase migration.")
        return
    
    try:
        # Step 1: Migrate accounts
        email_to_user_id = migrate_user_accounts()
        
        if not email_to_user_id:
            print("\n⚠️  No users were migrated. Cannot continue.")
            return
        
        # Step 2: Migrate memory
        migrate_user_memory(email_to_user_id)
        
        # Step 3: Migrate profiles
        migrate_community_profiles(email_to_user_id)
        
        # Step 4: Verify
        all_good = verify_migration(email_to_user_id)
        
        print("\n" + "=" * 60)
        if all_good:
            print("✓ Migration Complete!")
        else:
            print("⚠️  Migration completed with warnings")
        print("=" * 60)
        
        print("\nNext steps:")
        print("1. Verify data in Supabase dashboard")
        print("2. Test login with migrated users (they'll need to reset passwords)")
        print("3. Once verified, run cleanup script to remove JSON files")
        print("\nTo remove JSON files after verification, run:")
        print("  python cleanup_json_files.py")
        
    except Exception as e:
        print(f"\nERROR: Migration failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

