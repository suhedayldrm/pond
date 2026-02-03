#!/usr/bin/env python3
"""
Update Wortzerlegung Script
============================
Updates composition and decompositionMeaning fields by scraping
the actual Wortzerlegung section from DWDS pages.
Does NOT change any other data.

Usage:
  python update_wortzerlegung.py --level A1
  python update_wortzerlegung.py --all-levels
"""

import json
import argparse
import requests
import time
from pathlib import Path
from urllib.parse import unquote
from bs4 import BeautifulSoup, NavigableString
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# Prefix meanings dictionary
PREFIX_MEANINGS = {
    "ab": "off, away",
    "an": "on, to",
    "auf": "up, open",
    "aus": "out, off",
    "ein": "in, into",
    "mit": "with, along",
    "vor": "before, forward",
    "be": "makes transitive",
    "ge": "participle / past",
    "ent": "remove, away",
    "er": "achieve, complete",
    "ver": "excess, change",
    "zer": "destroy, apart",
    "um": "around / derail",
    "über": "over / translate",
    "unter": "under",
    "durch": "through",
    "hinter": "behind",
    "wider": "against",
    "miss": "wrong, bad",
    "hin": "toward",
    "her": "from",
    "zu": "to, closed",
    "nach": "after",
    "los": "loose, off"
}

# Suffix meanings dictionary
SUFFIX_MEANINGS = {
    "chen": "diminutive",
    "lein": "diminutive",
    "e": "verb→noun",
    "heit": "abstract noun",
    "keit": "abstract noun",
    "ling": "person/thing",
    "ung": "action/process",
    "bar": "capability",
    "er": "agent/doer",
    "ig": "quality",
    "lich": "characteristic",
    "los": "without",
    "sam": "tendency",
    "weise": "manner",
    "isch": "relating to",
    "or": "agent noun",
    "in": "feminine",
    "schaft": "collective/state",
    "tum": "state/realm",
    "nis": "result/state",
    "sal": "result",
    "t": "past participle",
    "en": "infinitive/plural",
    "end": "present participle",
    "haft": "having quality"
}


def fetch_dwds_page(word: str, max_retries: int = 3):
    """Fetch DWDS page for a word."""
    url = f"https://www.dwds.de/wb/{word}"
    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except requests.RequestException as e:
            if attempt < max_retries - 1:
                time.sleep(1)
            else:
                return None
    return None


def classify_part(part):
    """Classify a word part as prefix, suffix, or root and return its meaning."""
    clean_part = part.replace('-', '')
    if part.endswith('-'):
        meaning = PREFIX_MEANINGS.get(clean_part, clean_part)
        return f"prefix: {meaning}"
    elif part.startswith('-'):
        meaning = SUFFIX_MEANINGS.get(clean_part, clean_part)
        return f"suffix: {meaning}"
    else:
        return f"root word: {part}"


def get_wortzerlegung(soup, word: str):
    """
    Extract Wortzerlegung from DWDS page.
    Handles both linked parts (<a> tags) and plain text parts.
    Strips <sup> disambiguation numbers.

    Returns:
        tuple: (composition list, decomposition meanings list)
    """
    composition = []
    decomposition_meaning = []

    if not soup:
        return composition, decomposition_meaning

    ft_blocks = soup.find_all('div', class_='dwdswb-ft-block')
    for block in ft_blocks:
        label = block.find('span', class_='dwdswb-ft-blocklabel')
        if label and 'Wortzerlegung' in label.get_text():
            blocktext = block.find('span', class_='dwdswb-ft-blocktext')
            if blocktext:
                for child in blocktext.children:
                    if isinstance(child, NavigableString):
                        text = child.strip()
                        if text:
                            composition.append(text)
                            decomposition_meaning.append(classify_part(text))
                    elif child.name == 'a':
                        for sup in child.find_all('sup'):
                            sup.decompose()
                        part = child.get_text(strip=True)
                        if part:
                            composition.append(part)
                            decomposition_meaning.append(classify_part(part))
            break

    return composition, decomposition_meaning


def fetch_word_wortzerlegung(idx, word_data):
    """Fetch Wortzerlegung for a single word. Used in thread pool."""
    word = word_data.get('word', '')
    word_decoded = unquote(word)

    soup = fetch_dwds_page(word_decoded)
    composition, decomposition_meaning = get_wortzerlegung(soup, word_decoded)

    return idx, word_decoded, composition, decomposition_meaning


def update_level(level: str, batch_size: int = 10, max_workers: int = 5):
    """Update Wortzerlegung for a vocabulary level using batch processing."""

    file_path = Path(__file__).parent / "app" / "german" / f"{level}.json"

    if not file_path.exists():
        print(f"❌ File not found: {file_path}")
        return

    print(f"\n{'='*60}")
    print(f"Updating Wortzerlegung for {level}")
    print(f"Batch size: {batch_size}, Workers: {max_workers}")
    print(f"{'='*60}\n")

    with open(file_path, 'r', encoding='utf-8') as f:
        words = json.load(f)

    total = len(words)
    updated_count = 0

    # Load progress
    progress_file = Path(__file__).parent / f".wortzerlegung_progress_{level}.json"
    start_idx = 0
    if progress_file.exists():
        try:
            with open(progress_file, 'r') as f:
                progress = json.load(f)
                start_idx = progress.get('last_idx', 0)
                print(f"📍 Resuming from word {start_idx+1}")
        except:
            pass

    # Process in batches
    for batch_start in range(start_idx, total, batch_size):
        batch_end = min(batch_start + batch_size, total)
        batch = [(i, words[i]) for i in range(batch_start, batch_end)]

        print(f"[{batch_start+1}-{batch_end}/{total}] Processing batch...", end=" ")

        results = []
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(fetch_word_wortzerlegung, idx, word_data): idx
                      for idx, word_data in batch}

            for future in as_completed(futures):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    print(f"Error: {e}")

        # Apply results
        batch_updated = 0
        for idx, word_decoded, composition, decomposition_meaning in results:
            if composition:
                words[idx]['composition'] = composition
                words[idx]['decompositionMeaning'] = decomposition_meaning
                batch_updated += 1
            else:
                if 'composition' not in words[idx]:
                    words[idx]['composition'] = []
                if 'decompositionMeaning' not in words[idx]:
                    words[idx]['decompositionMeaning'] = []

        updated_count += batch_updated
        print(f"✓ {batch_updated} updated")

        # Save progress after each batch
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(words, f, indent=2, ensure_ascii=False)
        with open(progress_file, 'w') as f:
            json.dump({'last_idx': batch_end}, f)

    # Delete progress file
    if progress_file.exists():
        progress_file.unlink()

    print(f"\n{'='*60}")
    print(f"✅ {level} complete! Updated {updated_count}/{total} words")
    print(f"{'='*60}\n")


def main():
    parser = argparse.ArgumentParser(description='Update Wortzerlegung from DWDS')
    parser.add_argument('--level', type=str, choices=['A1', 'A2', 'B1', 'B2', 'C1', 'C2'],
                       help='Level to update')
    parser.add_argument('--all-levels', action='store_true',
                       help='Update all levels')

    args = parser.parse_args()

    if args.all_levels:
        for level in ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']:
            try:
                update_level(level)
            except Exception as e:
                print(f"❌ Error with {level}: {e}")
    elif args.level:
        update_level(args.level)
    else:
        print("Usage: python update_wortzerlegung.py --level A1")
        print("       python update_wortzerlegung.py --all-levels")


if __name__ == "__main__":
    main()
