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
from pathlib import Path
from deep_translator import GoogleTranslator

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
            time.sleep(0.3)  # Rate limiting
            return result
        except Exception as e:
            print(f"  ⚠️  Translation attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(2)
            else:
                return clean_text  # Return original if failed

    return clean_text


def add_translations_to_level(level: str):
    """Add translations to a vocabulary level"""

    file_path = Path(__file__).parent / "app" / "german" / f"{level}.json"

    if not file_path.exists():
        print(f"❌ File not found: {file_path}")
        return

    print(f"\n{'='*60}")
    print(f"Adding translations to {level}")
    print(f"{'='*60}\n")

    with open(file_path, 'r', encoding='utf-8') as f:
        words = json.load(f)

    total = len(words)
    translated_count = 0

    for idx, word_data in enumerate(words):
        word = word_data.get('word', '')
        print(f"[{idx+1}/{total}] Processing: {word}")

        needs_save = False

        # Translate main word if needed
        english = word_data.get('english', '')
        if english == word or not english:
            word_data['english'] = translate_text(word)
            needs_save = True
            print(f"  - Main word translated")

        # Translate examples if needed
        examples = word_data.get('examples', [])
        for ex in examples:
            if isinstance(ex, dict):
                german = ex.get('german', '')
                eng = ex.get('english', '')
                if eng == german or not eng:
                    ex['english'] = translate_text(german)
                    needs_save = True

        # Translate synonyms if needed (convert to {german, english} format)
        synonyms = word_data.get('synonyms', [])
        new_synonyms = []
        for syn in synonyms:
            if isinstance(syn, str):
                # String format - needs translation
                new_synonyms.append({
                    "german": syn,
                    "english": translate_text(syn)
                })
                needs_save = True
            elif isinstance(syn, dict):
                german = syn.get('german', '')
                eng = syn.get('english', '')
                if eng == german or not eng:
                    syn['english'] = translate_text(german)
                    needs_save = True
                new_synonyms.append(syn)

        if new_synonyms:
            word_data['synonyms'] = new_synonyms

        if needs_save:
            translated_count += 1

        # Save progress every 20 words
        if (idx + 1) % 20 == 0:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(words, f, indent=2, ensure_ascii=False)
            print(f"\n  💾 Progress saved ({idx+1}/{total})\n")

    # Final save
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(words, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*60}")
    print(f"✅ {level} complete! Translated {translated_count} words")
    print(f"{'='*60}\n")


def main():
    parser = argparse.ArgumentParser(description='Add translations to vocabulary data')
    parser.add_argument('--level', type=str, choices=['A1', 'A2', 'B1', 'B2', 'C1', 'C2'],
                       help='Level to translate')
    parser.add_argument('--all-levels', action='store_true',
                       help='Translate all levels')

    args = parser.parse_args()

    if args.all_levels:
        for level in ['A1', 'A2', 'B1', 'B2']:
            try:
                add_translations_to_level(level)
            except Exception as e:
                print(f"❌ Error with {level}: {e}")
    elif args.level:
        add_translations_to_level(args.level)
    else:
        print("Usage: python add_translations.py --level A1")
        print("       python add_translations.py --all-levels")


if __name__ == "__main__":
    main()
