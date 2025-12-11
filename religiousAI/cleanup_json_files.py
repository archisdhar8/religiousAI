"""
Cleanup Script: Remove JSON Files After Migration

This script removes the old JSON files after verifying data has been
successfully migrated to Supabase.

WARNING: This will permanently delete JSON files. Make sure you have:
1. Verified all data in Supabase dashboard
2. Tested the application with migrated users
3. Backed up the data directory (optional but recommended)

Usage:
    python cleanup_json_files.py
"""

import os
import shutil
from datetime import datetime
from config import BASE_DIR

# Directories to clean
USERS_DIR = os.path.join(BASE_DIR, "data", "users")
ACCOUNTS_DIR = os.path.join(BASE_DIR, "data", "accounts")
SESSIONS_DIR = os.path.join(BASE_DIR, "data", "sessions")
COMMUNITY_DIR = os.path.join(BASE_DIR, "data", "community")
PROFILES_DIR = os.path.join(COMMUNITY_DIR, "profiles")


def count_json_files(directory: str) -> int:
    """Count JSON files in a directory."""
    if not os.path.exists(directory):
        return 0
    return len([f for f in os.listdir(directory) if f.endswith('.json')])


def backup_directory(directory: str, backup_name: str) -> str:
    """Create a backup of a directory."""
    if not os.path.exists(directory):
        return None
    
    backup_path = os.path.join(BASE_DIR, "data", f"{backup_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    shutil.copytree(directory, backup_path)
    return backup_path


def cleanup_directory(directory: str, description: str) -> tuple[int, int]:
    """Remove JSON files from a directory."""
    if not os.path.exists(directory):
        return 0, 0
    
    deleted = 0
    errors = 0
    
    for filename in os.listdir(directory):
        if filename.endswith('.json'):
            filepath = os.path.join(directory, filename)
            try:
                os.remove(filepath)
                deleted += 1
            except Exception as e:
                print(f"    ✗ Error deleting {filename}: {e}")
                errors += 1
    
    return deleted, errors


def main():
    """Main cleanup function."""
    print("=" * 60)
    print("JSON Files Cleanup Script")
    print("=" * 60)
    
    # Count files
    users_count = count_json_files(USERS_DIR)
    accounts_count = count_json_files(ACCOUNTS_DIR)
    sessions_count = count_json_files(SESSIONS_DIR)
    profiles_count = count_json_files(PROFILES_DIR)
    
    total_files = users_count + accounts_count + sessions_count + profiles_count
    
    print(f"\nFound JSON files:")
    print(f"  - User memory files: {users_count}")
    print(f"  - Account files: {accounts_count}")
    print(f"  - Session files: {sessions_count}")
    print(f"  - Profile files: {profiles_count}")
    print(f"  - Total: {total_files}")
    
    if total_files == 0:
        print("\n✓ No JSON files found. Nothing to clean up.")
        return
    
    print("\n" + "=" * 60)
    print("IMPORTANT WARNINGS:")
    print("=" * 60)
    print("1. This will PERMANENTLY DELETE all JSON files")
    print("2. Make sure you have verified data in Supabase dashboard")
    print("3. Make sure you have tested the application")
    print("4. Consider creating a backup first")
    print()
    
    # Offer backup
    backup_choice = input("Create backup before deleting? (yes/no): ")
    backup_paths = []
    
    if backup_choice.lower() == "yes":
        print("\nCreating backups...")
        if users_count > 0:
            backup = backup_directory(USERS_DIR, "users_backup")
            if backup:
                backup_paths.append(backup)
                print(f"  ✓ Backed up users to: {backup}")
        
        if accounts_count > 0:
            backup = backup_directory(ACCOUNTS_DIR, "accounts_backup")
            if backup:
                backup_paths.append(backup)
                print(f"  ✓ Backed up accounts to: {backup}")
        
        if sessions_count > 0:
            backup = backup_directory(SESSIONS_DIR, "sessions_backup")
            if backup:
                backup_paths.append(backup)
                print(f"  ✓ Backed up sessions to: {backup}")
        
        if profiles_count > 0:
            backup = backup_directory(PROFILES_DIR, "profiles_backup")
            if backup:
                backup_paths.append(backup)
                print(f"  ✓ Backed up profiles to: {backup}")
    
    print("\n" + "=" * 60)
    confirm = input("Are you SURE you want to delete all JSON files? (type 'DELETE' to confirm): ")
    
    if confirm != "DELETE":
        print("Cleanup cancelled.")
        if backup_paths:
            print(f"\nBackups created at:")
            for path in backup_paths:
                print(f"  - {path}")
        return
    
    print("\n" + "=" * 60)
    print("Cleaning up JSON files...")
    print("=" * 60)
    
    total_deleted = 0
    total_errors = 0
    
    # Clean up each directory
    if users_count > 0:
        print(f"\nCleaning user memory files...")
        deleted, errors = cleanup_directory(USERS_DIR, "user memory")
        total_deleted += deleted
        total_errors += errors
        print(f"  Deleted: {deleted}, Errors: {errors}")
    
    if accounts_count > 0:
        print(f"\nCleaning account files...")
        deleted, errors = cleanup_directory(ACCOUNTS_DIR, "accounts")
        total_deleted += deleted
        total_errors += errors
        print(f"  Deleted: {deleted}, Errors: {errors}")
    
    if sessions_count > 0:
        print(f"\nCleaning session files...")
        deleted, errors = cleanup_directory(SESSIONS_DIR, "sessions")
        total_deleted += deleted
        total_errors += errors
        print(f"  Deleted: {deleted}, Errors: {errors}")
    
    if profiles_count > 0:
        print(f"\nCleaning profile files...")
        deleted, errors = cleanup_directory(PROFILES_DIR, "profiles")
        total_deleted += deleted
        total_errors += errors
        print(f"  Deleted: {deleted}, Errors: {errors}")
    
    print("\n" + "=" * 60)
    print("Cleanup Complete!")
    print("=" * 60)
    print(f"\nSummary:")
    print(f"  - Files deleted: {total_deleted}")
    print(f"  - Errors: {total_errors}")
    
    if backup_paths:
        print(f"\nBackups saved at:")
        for path in backup_paths:
            print(f"  - {path}")
        print("\nYou can delete these backups once you're confident the migration is successful.")


if __name__ == "__main__":
    main()

