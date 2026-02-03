#!/usr/bin/env python3
"""
Add Translations Script
========================
Adds English translations to already extracted vocabulary data.
Run this after extraction is complete and Google rate limit has reset.

Usage:
  python add_translations.py --level A1
  python add_translations.py --all-levels
"""

import json
import time
import argparse
import logging
from pathlib import Path
from datetime import datetime
from urllib.parse import unquote
from deep_translator import GoogleTranslator

# Setup logging
log_file = Path(__file__).parent / f"translation_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize translator
translator = GoogleTranslator(source='de', target='en')


def translate_text(german_text, max_retries=3):
    """Translate German text to English"""
    if not german_text:
        return ""

    clean_text = german_text.strip()

    for attempt in range(max_retries):
        try:
            result = translator.translate(clean_text)
            time.sleep(0.1)  # Rate limiting
            return result
        except Exception as e:
            logger.warning(f"Translation attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(2)
            else:
                return clean_text  # Return original if failed

    return clean_text


def translate_batch(texts, max_retries=3):
    """Translate multiple texts in one API call using delimiter, with chunking for API limits"""
    if not texts:
        return []

    # Filter empty texts and keep track of indices
    valid_texts = [(i, t.strip()) for i, t in enumerate(texts) if t and t.strip()]
    if not valid_texts:
        return [""] * len(texts)

    DELIMITER = " ||| "
    MAX_CHARS = 4500  # Google Translate limit is 5000, leave buffer

    # Split into chunks that fit within character limit
    chunks = []
    current_chunk = []
    current_length = 0

    for idx, text in valid_texts:
        text_length = len(text) + len(DELIMITER)
        if current_length + text_length > MAX_CHARS and current_chunk:
            chunks.append(current_chunk)
            current_chunk = []
            current_length = 0
        current_chunk.append((idx, text))
        current_length += text_length

    if current_chunk:
        chunks.append(current_chunk)

    # Translate each chunk
    final_result = [""] * len(texts)

    for chunk in chunks:
        combined = DELIMITER.join([t for _, t in chunk])

        for attempt in range(max_retries):
            try:
                result = translator.translate(combined)
                time.sleep(0.2)  # Rate limit

                translated_parts = result.split("|||")
                translated_parts = [p.strip() for p in translated_parts]

                for idx, (orig_idx, orig_text) in enumerate(chunk):
                    if idx < len(translated_parts):
                        final_result[orig_idx] = translated_parts[idx]
                    else:
                        final_result[orig_idx] = orig_text
                break
            except Exception as e:
                logger.warning(f"Chunk translation attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2)
                else:
                    for orig_idx, orig_text in chunk:
                        final_result[orig_idx] = orig_text

    return final_result


def add_translations_to_level(level: str):
    """Add translations to a vocabulary level - translates synonyms and examples only"""

    file_path = Path(__file__).parent / "app" / "german" / f"{level}.json"

    if not file_path.exists():
        logger.error(f"File not found: {file_path}")
        return

    logger.info(f"{'='*60}")
    logger.info(f"Adding translations to {level}")
    logger.info(f"{'='*60}")

    with open(file_path, 'r', encoding='utf-8') as f:
        words = json.load(f)

    total = len(words)
    translated_count = 0
    main_count = 0
    synonym_count = 0
    example_count = 0
    BATCH_SIZE = 30

    # Load progress from file
    progress_file = Path(__file__).parent / f".translation_progress_{level}.json"
    start_batch = 0
    if progress_file.exists():
        try:
            with open(progress_file, 'r') as f:
                progress = json.load(f)
                start_batch = progress.get('last_batch', 0)
                logger.info(f"Resuming from word {start_batch+1}")
        except:
            pass

    if start_batch >= total:
        logger.info(f"All words already translated!")
        return

    for batch_start in range(start_batch, total, BATCH_SIZE):
        batch_end = min(batch_start + BATCH_SIZE, total)
        batch_words = words[batch_start:batch_end]

        # Collect all texts from all words in batch
        all_texts = []
        all_mappings = []  # (word_idx, text_type, text_idx)

        for word_idx, word_data in enumerate(batch_words):
            # 0. Translate main english field (when it equals word or is empty)
            word = word_data.get('word', '')
            english = word_data.get('english', '')
            decoded_word = unquote(word)
            decoded_english = unquote(english) if english else ''
            if word and (not english or english == word or decoded_english == decoded_word):
                all_texts.append(decoded_word)
                all_mappings.append((word_idx, 'main_english', 0))

            # 1. Translate synonyms (when english equals german or is empty)
            synonyms = word_data.get('synonyms', [])
            for i, syn in enumerate(synonyms):
                if isinstance(syn, dict):
                    german = syn.get('german', '')
                    english = syn.get('english', '')
                    # Translate if english is same as german or empty
                    if german and (not english or english == german):
                        all_texts.append(german)
                        all_mappings.append((word_idx, 'synonym', i))

            # 2. Translate examples (when english equals german or is empty)
            examples = word_data.get('examples', [])
            for i, ex in enumerate(examples):
                if isinstance(ex, dict):
                    german = ex.get('german', '')
                    english = ex.get('english', '')
                    # Translate if english is same as german or empty
                    if german and (not english or english == german):
                        all_texts.append(german)
                        all_mappings.append((word_idx, 'example', i))

        # Skip batch if nothing to translate
        if not all_texts:
            with open(progress_file, 'w') as f:
                json.dump({'last_batch': batch_end}, f)
            continue

        logger.info(f"[{batch_start+1}-{batch_end}/{total}] Translating {len(all_texts)} items...")

        # Batch translate all at once
        translations = translate_batch(all_texts)

        # Apply translations back
        for i, (word_idx, text_type, text_idx) in enumerate(all_mappings):
            word_data = batch_words[word_idx]
            if i < len(translations):
                if text_type == 'main_english':
                    word_data['english'] = translations[i]
                    main_count += 1
                elif text_type == 'synonym':
                    word_data['synonyms'][text_idx]['english'] = translations[i]
                    synonym_count += 1
                elif text_type == 'example':
                    word_data['examples'][text_idx]['english'] = translations[i]
                    example_count += 1

        translated_count += len(batch_words)

        # Save progress every batch
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(words, f, indent=2, ensure_ascii=False)
        with open(progress_file, 'w') as f:
            json.dump({'last_batch': batch_end}, f)
        logger.info(f"  Saved ({batch_end}/{total})")

    # Final save
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(words, f, indent=2, ensure_ascii=False)

    # Delete progress file when done
    if progress_file.exists():
        progress_file.unlink()

    logger.info(f"{'='*60}")
    logger.info(f"{level} complete! Main: {main_count}, Synonyms: {synonym_count}, Examples: {example_count}")
    logger.info(f"{'='*60}")


def main():
    parser = argparse.ArgumentParser(description='Add translations to vocabulary data')
    parser.add_argument('--level', type=str, choices=['A1', 'A2', 'B1', 'B2', 'C1', 'C2'],
                       help='Level to translate')
    parser.add_argument('--all-levels', action='store_true',
                       help='Translate all levels')

    args = parser.parse_args()

    logger.info(f"Translation started - Log file: {log_file}")

    if args.all_levels:
        for level in ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']:
            try:
                add_translations_to_level(level)
            except Exception as e:
                logger.error(f"Error with {level}: {e}")
    elif args.level:
        add_translations_to_level(args.level)
    else:
        print("Usage: python add_translations.py --level A1")
        print("       python add_translations.py --all-levels")

    logger.info("Translation completed")


if __name__ == "__main__":
    main()
