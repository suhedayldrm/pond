#!/usr/bin/env python3
"""Parallel extraction script - runs multiple workers for faster extraction"""

import json
import multiprocessing
import sys
from pathlib import Path
from extract_dwds_data import extract_word_data_scraping, load_german_base_data

def process_chunk(args):
    """Process a chunk of words"""
    worker_id, level, words_chunk, base_data = args
    results = []

    for idx, word in enumerate(words_chunk):
        print(f"[Worker {worker_id}] [{idx+1}/{len(words_chunk)}] Processing: {word}")
        try:
            r = extract_word_data_scraping(word, base_data.get(word))
            if r:
                results.append(r)
        except Exception as e:
            print(f"[Worker {worker_id}] Error processing {word}: {e}")

    print(f"[Worker {worker_id}] Done! Processed {len(results)} words")
    return results

def run_parallel_extraction(level, start_from, num_workers=4):
    """Run extraction in parallel using multiple workers"""

    # Load base data
    base_data = load_german_base_data(level)
    all_words = list(base_data.keys())
    total_words = len(all_words)

    words_to_process = all_words[start_from:]
    words_left = len(words_to_process)
    chunk_size = words_left // num_workers

    print(f"Starting parallel extraction for {level}")
    print(f"Total words: {total_words}, Starting from: {start_from}")
    print(f"Words left: {words_left}, Workers: {num_workers}")
    print(f"Chunk size: ~{chunk_size} words per worker\n")

    # Split into chunks
    chunks = []
    for i in range(num_workers):
        start_idx = i * chunk_size
        if i == num_workers - 1:
            end_idx = words_left
        else:
            end_idx = (i + 1) * chunk_size
        chunk = words_to_process[start_idx:end_idx]
        chunks.append((i, level, chunk, base_data))
        print(f"Worker {i}: {len(chunk)} words")

    print("\nStarting workers...")

    # Run in parallel
    with multiprocessing.Pool(num_workers) as pool:
        all_results = pool.map(process_chunk, chunks)

    # Flatten results
    merged = []
    for chunk_results in all_results:
        merged.extend(chunk_results)

    print(f"\nAll workers done! Total new words: {len(merged)}")

    # Load existing data and merge
    output_file = Path(__file__).parent / "app" / "german" / f"{level}.json"
    with open(output_file) as f:
        existing = json.load(f)

    existing.extend(merged)

    # Save
    with open(output_file, 'w') as f:
        json.dump(existing, f, indent=2, ensure_ascii=False)

    print(f"Saved {len(existing)} total words to {output_file}")

if __name__ == "__main__":
    level = sys.argv[1] if len(sys.argv) > 1 else "B1"
    start = int(sys.argv[2]) if len(sys.argv) > 2 else 400
    workers = int(sys.argv[3]) if len(sys.argv) > 3 else 4
    run_parallel_extraction(level, start, workers)
