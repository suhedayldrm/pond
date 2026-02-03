#!/usr/bin/env python3
"""
Re-extract vocabulary for B2, C1, C2 by randomly selecting words from base files.
Uses parallel processing for speed.
"""

import json
import random
import time
import sys
import multiprocessing
from pathlib import Path
from datetime import datetime
from extract_dwds_data import extract_word_data_scraping

BASE_DIR = Path(__file__).parent / "app" / "german_base"
OUTPUT_DIR = Path(__file__).parent / "app" / "german"

# How many words to extract per level
TARGET_COUNTS = {
    "B2": 3000,
    "C1": 3000,
    "C2": 3000,
}

def load_and_filter_base(level):
    """Load base file and filter to real words (starts with a letter)."""
    base_file = BASE_DIR / f"{level}.json"
    with open(base_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Filter: keep only entries whose lemma starts with a letter
    filtered = [item for item in data if item.get("lemma") and item["lemma"][0:1].isalpha()]
    print(f"{level}: {len(data)} total base entries, {len(filtered)} valid words (start with letter)")
    return filtered


def scrape_chunk(args):
    """Worker function: scrape a chunk of words."""
    worker_id, words_with_data, level = args
    results = []
    for idx, (lemma, pos_data) in enumerate(words_with_data):
        try:
            result = extract_word_data_scraping(lemma, pos_data=pos_data, debug=False)
            if result:
                results.append(result)
                if (idx + 1) % 20 == 0:
                    print(f"  [Worker {worker_id}] {idx+1}/{len(words_with_data)} done ({len(results)} successful)")
            else:
                print(f"  [Worker {worker_id}] Failed: {lemma}")
        except Exception as e:
            print(f"  [Worker {worker_id}] Error on {lemma}: {e}")
    print(f"  [Worker {worker_id}] Finished: {len(results)}/{len(words_with_data)} successful")
    return results


def extract_level(level, num_workers=6):
    """Randomly select and scrape words for a level."""
    target = TARGET_COUNTS[level]
    filtered = load_and_filter_base(level)

    if len(filtered) <= target:
        selected = filtered
        print(f"{level}: Base has fewer words ({len(filtered)}) than target ({target}), using all")
    else:
        selected = random.sample(filtered, target)
        print(f"{level}: Randomly selected {target} from {len(filtered)} words")

    # Verify distribution
    letter_counts = {}
    for item in selected:
        letter = item["lemma"][0].upper()
        letter_counts[letter] = letter_counts.get(letter, 0) + 1
    top_5 = sorted(letter_counts.items(), key=lambda x: -x[1])[:5]
    print(f"{level}: Top 5 starting letters: {top_5}")

    # Prepare word list with POS data
    words_with_data = []
    for item in selected:
        lemma = item["lemma"]
        pos_data = {
            "pos": item.get("wortklasse", "unknown"),
            "url": item.get("url", ""),
            "level": item.get("level", level),
        }
        words_with_data.append((lemma, pos_data))

    # Split into chunks for parallel processing
    chunk_size = len(words_with_data) // num_workers
    chunks = []
    for i in range(num_workers):
        start = i * chunk_size
        end = len(words_with_data) if i == num_workers - 1 else (i + 1) * chunk_size
        chunks.append((i, words_with_data[start:end], level))
        print(f"  Worker {i}: {end - start} words")

    print(f"\nStarting {num_workers} workers for {level}...")
    start_time = time.time()

    with multiprocessing.Pool(num_workers) as pool:
        all_results = pool.map(scrape_chunk, chunks)

    # Merge results
    merged = []
    for chunk_results in all_results:
        merged.extend(chunk_results)

    elapsed = time.time() - start_time
    print(f"\n{level} done: {len(merged)} words scraped in {elapsed:.0f}s")

    # Verify final distribution
    final_letters = {}
    for w in merged:
        letter = w.get("word", "?")[0].upper()
        final_letters[letter] = final_letters.get(letter, 0) + 1
    top_5_final = sorted(final_letters.items(), key=lambda x: -x[1])[:5]
    print(f"{level} final top 5 letters: {top_5_final}")

    # Save
    output_file = OUTPUT_DIR / f"{level}.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(merged, f, indent=2, ensure_ascii=False)
    print(f"{level}: Saved {len(merged)} words to {output_file}")

    return merged


if __name__ == "__main__":
    levels = sys.argv[1:] if len(sys.argv) > 1 else ["B2", "C1", "C2"]

    log_file = Path(__file__).parent / f"reextract_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

    print(f"Re-extracting levels: {levels}")
    print(f"Log: {log_file}")
    print(f"Started: {datetime.now()}")
    print("=" * 60)

    for level in levels:
        if level in TARGET_COUNTS:
            print(f"\n{'='*60}")
            print(f"Processing {level}")
            print(f"{'='*60}")
            extract_level(level)
        else:
            print(f"Skipping {level} - not in target list")

    print(f"\nAll done: {datetime.now()}")
