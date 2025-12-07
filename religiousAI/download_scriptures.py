#!/usr/bin/env python3
"""
Scripture Download Helper for Divine Wisdom Guide

This script helps download public domain religious texts from various sources.
All texts are in the public domain or freely available for educational use.

Usage:
    python download_scriptures.py [--all] [--tradition NAME]
    
Examples:
    python download_scriptures.py --all           # Download all available scriptures
    python download_scriptures.py --tradition buddhism  # Download only Buddhist texts
    python download_scriptures.py --list          # List available scriptures
"""

import os
import sys
import urllib.request
import ssl
from typing import Dict, List, Optional

# Disable SSL verification for downloads (some sources have certificate issues)
ssl._create_default_https_context = ssl._create_unverified_context

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_DATA_DIR = os.path.join(BASE_DIR, "data", "raw")

# ============================================================================
# SCRIPTURE SOURCES
# All texts are public domain or freely available for educational purposes
# ============================================================================

SCRIPTURES: Dict[str, List[Dict]] = {
    "Christianity": [
        {
            "name": "bible_kjv.txt",
            "description": "King James Bible (1611) - Complete Old and New Testament",
            "url": "https://www.gutenberg.org/cache/epub/10/pg10.txt",
            "source": "Project Gutenberg"
        },
        {
            "name": "bible_asv.txt",
            "description": "American Standard Version Bible (1901)",
            "url": "https://www.gutenberg.org/cache/epub/100/pg100.txt",
            "source": "Project Gutenberg"
        }
    ],
    "Hinduism": [
        {
            "name": "bhagavad_gita.txt",
            "description": "Bhagavad Gita - Song of the Lord (Edwin Arnold translation)",
            "url": "https://www.gutenberg.org/cache/epub/2388/pg2388.txt",
            "source": "Project Gutenberg"
        },
        {
            "name": "upanishads.txt",
            "description": "Principal Upanishads (Max Müller translation)",
            "url": "https://www.gutenberg.org/cache/epub/3283/pg3283.txt",
            "source": "Project Gutenberg"
        },
        {
            "name": "ramayana.txt",
            "description": "The Ramayana - Epic of Rama",
            "url": "https://www.gutenberg.org/cache/epub/24869/pg24869.txt",
            "source": "Project Gutenberg"
        }
    ],
    "Buddhism": [
        {
            "name": "dhammapada.txt",
            "description": "Dhammapada - Sayings of the Buddha (Max Müller translation)",
            "url": "https://www.gutenberg.org/cache/epub/2017/pg2017.txt",
            "source": "Project Gutenberg"
        },
        {
            "name": "buddhist_sutras.txt",
            "description": "Buddhist Sutras - Sacred Books of the East selection",
            "url": "https://www.gutenberg.org/cache/epub/44336/pg44336.txt",
            "source": "Project Gutenberg"
        }
    ],
    "Taoism": [
        {
            "name": "tao_te_ching.txt",
            "description": "Tao Te Ching - The Way and Its Power (James Legge translation)",
            "url": "https://www.gutenberg.org/cache/epub/216/pg216.txt",
            "source": "Project Gutenberg"
        }
    ],
    "Islam": [
        {
            "name": "quran.txt",
            "description": "The Quran (M.H. Shakir translation - public domain)",
            "url": "https://www.gutenberg.org/cache/epub/7440/pg7440.txt",
            "source": "Project Gutenberg"
        }
    ],
    "Judaism": [
        {
            "name": "torah.txt",
            "description": "Torah / Pentateuch (from KJV - Genesis through Deuteronomy)",
            "url": None,  # Extracted from Bible
            "source": "Derived from KJV",
            "note": "Will be extracted from the Bible if available"
        },
        {
            "name": "talmud_selections.txt",
            "description": "Babylonian Talmud - Selections (Rodkinson translation)",
            "url": "https://www.gutenberg.org/cache/epub/6219/pg6219.txt",
            "source": "Project Gutenberg"
        }
    ],
    "Confucianism": [
        {
            "name": "analects.txt",
            "description": "Analects of Confucius (James Legge translation)",
            "url": "https://www.gutenberg.org/cache/epub/3330/pg3330.txt",
            "source": "Project Gutenberg"
        }
    ],
    "Zoroastrianism": [
        {
            "name": "avesta.txt",
            "description": "Zend-Avesta - Sacred texts of Zoroastrianism",
            "url": "https://www.gutenberg.org/cache/epub/22931/pg22931.txt",
            "source": "Project Gutenberg"
        }
    ],
    "Ancient_Wisdom": [
        {
            "name": "meditations_aurelius.txt",
            "description": "Meditations by Marcus Aurelius - Stoic Philosophy",
            "url": "https://www.gutenberg.org/cache/epub/2680/pg2680.txt",
            "source": "Project Gutenberg"
        },
        {
            "name": "enchiridion.txt",
            "description": "Enchiridion by Epictetus - Stoic Handbook",
            "url": "https://www.gutenberg.org/cache/epub/45109/pg45109.txt",
            "source": "Project Gutenberg"
        }
    ]
}


def print_header():
    print("=" * 70)
    print("🕊️  DIVINE WISDOM GUIDE - Scripture Downloader")
    print("=" * 70)
    print()


def list_scriptures():
    """List all available scriptures."""
    print_header()
    print("Available scriptures for download:\n")
    
    for tradition, texts in SCRIPTURES.items():
        icon = get_tradition_icon(tradition)
        print(f"\n{icon} {tradition.upper()}")
        print("-" * 40)
        for text in texts:
            status = "✓" if os.path.exists(os.path.join(RAW_DATA_DIR, text['name'])) else "○"
            print(f"  {status} {text['name']}")
            print(f"      {text['description']}")
    
    print("\n" + "=" * 70)
    print("✓ = Already downloaded   ○ = Available for download")
    print("=" * 70)


def get_tradition_icon(tradition: str) -> str:
    icons = {
        "Christianity": "✝️",
        "Hinduism": "🕉️",
        "Buddhism": "☸️",
        "Taoism": "☯️",
        "Islam": "☪️",
        "Judaism": "✡️",
        "Confucianism": "📜",
        "Zoroastrianism": "🔥",
        "Ancient_Wisdom": "🏛️",
        "Sikhism": "🙏"
    }
    return icons.get(tradition, "📖")


def download_file(url: str, filepath: str, description: str) -> bool:
    """Download a file from URL to filepath."""
    try:
        print(f"  ⏳ Downloading: {description[:50]}...")
        
        # Create request with headers to avoid 403 errors
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        request = urllib.request.Request(url, headers=headers)
        
        with urllib.request.urlopen(request, timeout=60) as response:
            content = response.read()
            
            # Try to decode as UTF-8, fallback to latin-1
            try:
                text = content.decode('utf-8')
            except UnicodeDecodeError:
                text = content.decode('latin-1')
            
            # Clean up the text
            text = clean_gutenberg_text(text)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(text)
        
        size_kb = os.path.getsize(filepath) / 1024
        print(f"  ✓ Downloaded: {os.path.basename(filepath)} ({size_kb:.1f} KB)")
        return True
        
    except Exception as e:
        print(f"  ❌ Failed: {e}")
        return False


def clean_gutenberg_text(text: str) -> str:
    """Remove Project Gutenberg headers and footers."""
    lines = text.split('\n')
    
    # Find content start (after "START OF" marker)
    start_idx = 0
    for i, line in enumerate(lines):
        if '*** START OF' in line.upper() or '***START OF' in line.upper():
            start_idx = i + 1
            break
    
    # Find content end (before "END OF" marker)
    end_idx = len(lines)
    for i in range(len(lines) - 1, -1, -1):
        if '*** END OF' in lines[i].upper() or '***END OF' in lines[i].upper():
            end_idx = i
            break
    
    # Extract main content
    content_lines = lines[start_idx:end_idx]
    
    # Remove excessive blank lines
    cleaned = []
    blank_count = 0
    for line in content_lines:
        if line.strip() == '':
            blank_count += 1
            if blank_count <= 2:
                cleaned.append(line)
        else:
            blank_count = 0
            cleaned.append(line)
    
    return '\n'.join(cleaned)


def download_tradition(tradition: str) -> int:
    """Download all scriptures for a tradition. Returns count of downloaded files."""
    if tradition not in SCRIPTURES:
        print(f"❌ Unknown tradition: {tradition}")
        print(f"   Available: {', '.join(SCRIPTURES.keys())}")
        return 0
    
    icon = get_tradition_icon(tradition)
    print(f"\n{icon} Downloading {tradition} scriptures...")
    print("-" * 50)
    
    downloaded = 0
    for text in SCRIPTURES[tradition]:
        filepath = os.path.join(RAW_DATA_DIR, text['name'])
        
        # Skip if already exists
        if os.path.exists(filepath):
            print(f"  ⏭️  Already exists: {text['name']}")
            continue
        
        # Skip if no URL (like Torah which is derived)
        if text.get('url') is None:
            print(f"  ⏭️  Skipping (no direct URL): {text['name']}")
            if text.get('note'):
                print(f"      Note: {text['note']}")
            continue
        
        if download_file(text['url'], filepath, text['description']):
            downloaded += 1
    
    return downloaded


def download_all():
    """Download all available scriptures."""
    print_header()
    
    # Create data directory if needed
    os.makedirs(RAW_DATA_DIR, exist_ok=True)
    print(f"📁 Download directory: {RAW_DATA_DIR}\n")
    
    total_downloaded = 0
    
    for tradition in SCRIPTURES.keys():
        count = download_tradition(tradition)
        total_downloaded += count
    
    print("\n" + "=" * 70)
    if total_downloaded > 0:
        print(f"✨ SUCCESS! Downloaded {total_downloaded} new scripture(s)")
        print("\nNext steps:")
        print("  1. Run: python build_index.py")
        print("  2. Run: streamlit run app.py")
    else:
        print("ℹ️  No new scriptures downloaded (all already present)")
    print("=" * 70)


def main():
    args = sys.argv[1:]
    
    if '--help' in args or '-h' in args:
        print(__doc__)
        return
    
    if '--list' in args:
        list_scriptures()
        return
    
    if '--all' in args:
        download_all()
        return
    
    if '--tradition' in args:
        try:
            idx = args.index('--tradition')
            tradition = args[idx + 1]
            # Match case-insensitively
            for t in SCRIPTURES.keys():
                if t.lower() == tradition.lower():
                    tradition = t
                    break
            
            print_header()
            os.makedirs(RAW_DATA_DIR, exist_ok=True)
            download_tradition(tradition)
        except (IndexError, ValueError):
            print("Error: Please specify a tradition name")
            print("Usage: python download_scriptures.py --tradition buddhism")
        return
    
    # Default: show help
    print(__doc__)
    print("\nQuick start:")
    print("  python download_scriptures.py --all")
    print("\nOr see available scriptures:")
    print("  python download_scriptures.py --list")


if __name__ == "__main__":
    main()

