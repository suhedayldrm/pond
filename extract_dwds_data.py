#!/usr/bin/env python3
"""
DWDS German Vocabulary Extractor (Web Scraping Version)
========================================================
Extracts comprehensive German vocabulary data from DWDS (Digitales Wörterbuch der deutschen Sprache)
using web scraping to get rich data including etymology, compounds, examples, and related words.

Uses:
- BeautifulSoup for HTML parsing and data extraction
- Google Translate for English translations
- DWDS web pages for complete vocabulary information

Author: Claude Code
Date: 2026-01-13
"""

import requests
import json
import time
import re
from pathlib import Path
from urllib.parse import unquote
from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator
from typing import Optional, Dict, List, Tuple

# Initialize translator
translator = GoogleTranslator(source='de', target='en')

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
    "über": "over / translate"
}

# Suffix meanings dictionary
SUFFIX_MEANINGS = {
    "chen": "diminutives",
    "lein": "diminutives",
    "e": "verb→noun",
    "heit": "abstract nouns",
    "keit": "abstract nouns",
    "ling": "person associated",
    "ung": "action/process",
    "bar": "capability/possibility",
    "er": "noun-derived (adj.)",
    "ig": "quality/characteristic",
    "lich": "characteristic/manner",
    "los": "absence",
    "sam": "tendency/quality",
    "weise": "way/manner",
    "isch": "relationship/belonging",
    "or": "profession noun",
    "in": "feminine nouns"
}

# Part of speech mapping
POS_MAPPING = {
    'Substantiv': 'noun',
    'Verb': 'verb',
    'Adjektiv': 'adjective',
    'Adverb': 'adverb',
    'Konjunktion': 'conjunction',
    'Präposition': 'preposition',
    'Pronomen': 'pronoun',
    'Artikel': 'article',
    'Numerale': 'numeral',
    'Interjektion': 'interjection'
}


def translate_to_english(german_text, max_retries=3):
    """
    Translate German text to English using Google Translate.
    Currently disabled - returns original German text.
    """
    if not german_text:
        return ""
    return german_text.strip()


def fetch_dwds_page(url: str, max_retries: int = 3) -> Optional[BeautifulSoup]:
    """
    Fetch and parse DWDS page.

    Args:
        url: Page URL
        max_retries: Maximum retry attempts

    Returns:
        BeautifulSoup: Parsed HTML or None if failed
    """
    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except requests.RequestException as e:
            if attempt < max_retries - 1:
                time.sleep(1)
                continue
            else:
                print(f"  ⚠️  Page request failed for {url}: {e}")
                return None
    return None


def extract_word_from_lemma(lemma: str) -> str:
    """
    Extract clean word from lemma (removes articles, #1 suffixes, etc.)

    Args:
        lemma: Lemma string from DWDS

    Returns:
        str: Clean word
    """
    # Remove #1, #2, etc. suffixes (used to distinguish homonyms)
    word = re.sub(r'#\d+$', '', lemma)
    # Remove articles (der, die, das) and clean up
    word = re.sub(r',\s*(der|die|das)$', '', word)
    return word.strip()


def get_word_composition(word: str) -> Tuple[List[str], List[str]]:
    """
    Analyze word composition from morphemes.

    Args:
        word: German word

    Returns:
        tuple: (composition list, decomposition meanings list)
    """
    composition = []
    decomposition_meaning = []

    # Simple prefix detection
    for prefix in PREFIX_MEANINGS.keys():
        if word.startswith(prefix) and len(word) > len(prefix):
            composition.append(f"{prefix}-")
            decomposition_meaning.append(f"prefix: {PREFIX_MEANINGS[prefix]}")
            remaining = word[len(prefix):]
            if remaining:
                composition.append(remaining)
                try:
                    translated = translate_to_english(remaining)
                    decomposition_meaning.append(f"root word: {translated}")
                except:
                    decomposition_meaning.append("root word")
            break

    # Simple suffix detection if no prefix found
    if not composition:
        for suffix in SUFFIX_MEANINGS.keys():
            if word.endswith(suffix) and len(word) > len(suffix):
                remaining = word[:-len(suffix)]
                composition.append(remaining)
                composition.append(f"-{suffix}")
                try:
                    translated = translate_to_english(remaining)
                    decomposition_meaning.append(f"root word: {translated}")
                except:
                    decomposition_meaning.append("root word")
                decomposition_meaning.append(f"suffix: {SUFFIX_MEANINGS[suffix]}")
                break

    return composition, decomposition_meaning


def extract_word_data_scraping(word: str, pos_data: Optional[Dict] = None, debug: bool = False) -> Optional[Dict]:
    """
    Extract comprehensive German word information using web scraping.

    Args:
        word: German word/lemma to look up
        pos_data: Dictionary containing pos and other data from base JSON
        debug: Print debug information

    Returns:
        dict: Dictionary containing word information in the desired format with etymology, compounds, examples, and related words
    """
    try:
        if debug:
            print("=== DEBUG INFO ===")
            print(f"Looking up word: {word}")

        # Clean word (remove articles)
        clean_word = extract_word_from_lemma(word)

        # Fetch the DWDS page
        url = f"https://www.dwds.de/wb/{clean_word}"
        soup = fetch_dwds_page(url)

        if not soup:
            print(f"  ⚠️  Failed to fetch page for {clean_word}")
            return None

        # Extract part of speech
        part_of_speech = "unknown"
        if pos_data and 'pos' in pos_data:
            german_pos = pos_data['pos']
            part_of_speech = POS_MAPPING.get(german_pos, german_pos.lower())

        # Get word composition
        composition, decomposition_meaning = get_word_composition(clean_word)

        # Extract frequency (shown as visual dots)
        frequency = None
        freq_table = soup.find('table', class_='word-frequency')
        if freq_table:
            # Count the number of active frequency indicators
            active_dots = freq_table.find_all('div', class_='word-frequency-active')
            total_dots = len(freq_table.find_all('div', class_=lambda x: x and 'word-frequency' in x))
            if total_dots > 0:
                frequency = f"{len(active_dots)} out of {total_dots}"

        # Translate the word to English
        english_translation = translate_to_english(clean_word)

        # Extract etymology
        etymology = None
        # Find the etymology header
        etym_header = soup.find('h2', id=lambda x: x and x.startswith('etymwb'))
        if etym_header:
            # Find the etymwb-wrapper or etymwb-entry after the header
            etym_wrapper = etym_header.find_next('div', class_='etymwb-wrapper')
            if etym_wrapper:
                etym_entry = etym_wrapper.find('div', class_='etymwb-entry')
                if etym_entry:
                    # Get just the first sentence/portion for brevity
                    etymology_text = etym_entry.get_text(strip=True)
                    # Truncate to first 500 chars for manageability
                    if len(etymology_text) > 500:
                        etymology_text = etymology_text[:500] + "..."
                    # Translate to English
                    etymology = translate_to_english(etymology_text)

        # Extract example sentences (5-6 examples)
        examples = []
        # Find all example containers - both kompetenzbeispiel and beleg
        example_containers = soup.find_all('div', class_=['dwdswb-kompetenzbeispiel', 'dwdswb-beleg'], limit=15)

        example_count = 0
        for container in example_containers:
            if example_count >= 6:
                break
            # Extract the text from dwdswb-belegtext span
            beleg_text = container.find('span', class_='dwdswb-belegtext')
            if beleg_text:
                # Use separator to handle the dwdswb-stichwort spans properly
                german_example = beleg_text.get_text(separator=' ', strip=True)
                if german_example and len(german_example) > 5:
                    # Remove citation markers and clean up
                    german_example = re.sub(r'\[\d+\]', '', german_example).strip()
                    # Clean up multiple spaces
                    german_example = re.sub(r'\s+', ' ', german_example)
                    # Skip if it's just a word fragment (needs at least 2 words)
                    if ' ' in german_example:  # Must be a phrase/sentence
                        english_example = translate_to_english(german_example)
                        examples.append({
                            "german": german_example,
                            "english": english_example
                        })
                        example_count += 1

        # Extract compound words (Wortbildung)
        compounds = []
        # Find the ft-block containing "Wortbildung"
        ft_blocks = soup.find_all('div', class_='dwdswb-ft-block')
        for block in ft_blocks:
            label = block.find('span', class_='dwdswb-ft-blocklabel')
            if label and 'Wortbildung' in label.get_text():
                # Get the blocktext which contains the compound links
                blocktext = block.find('span', class_='dwdswb-ft-blocktext')
                if blocktext:
                    # Find all links to compound words
                    compound_links = blocktext.find_all('a', href=lambda x: x and x.startswith('/wb/'), limit=15)
                    for link in compound_links:
                        compound_word = link.get_text(strip=True)
                        if compound_word and compound_word != clean_word:
                            compounds.append(compound_word)
                break  # Found Wortbildung section, no need to continue

        # Skip collocations - use empty array (will be filled with extra examples in app)
        connected_words = []

        # Extract semantically related words from "Bedeutungsverwandte Ausdrücke" (synonyms/thesaurus)
        synonyms = []
        synonyms_set = set()  # Track already added words

        # Find "Bedeutungsverwandte Ausdrücke" section (ot-1, ot-2, etc.)
        ot_header = soup.find('h2', id=lambda x: x and x.startswith('ot-'))
        if ot_header:
            # Find all synset blocks after the header
            synset_blocks = soup.find_all('div', class_='ot-synset-block')
            for block in synset_blocks:
                # Find all synonym links within the block
                synonym_links = block.find_all('a', href=lambda x: x and '/wb/' in x, limit=20)
                for link in synonym_links:
                    german_word = link.get_text(strip=True)
                    if german_word and german_word != clean_word and german_word not in synonyms_set:
                        english_word = translate_to_english(german_word)
                        synonyms.append({
                            "german": german_word,
                            "english": english_word
                        })
                        synonyms_set.add(german_word)
                # Limit total synonyms to 15
                if len(synonyms) >= 15:
                    break

        # Return comprehensive data structure
        result = {
            "word": clean_word,
            "partOfSpeech": part_of_speech,
            "english": english_translation,
            "composition": composition if composition else [],
            "decompositionMeaning": decomposition_meaning if decomposition_meaning else [],
            "frequency": frequency,
            "connected_words": connected_words,
            "synonyms": synonyms,
            "examples": examples,
            "etymology": etymology,
            "compounds": compounds,
            "source_url": unquote(url)
        }

        return result

    except Exception as e:
        print(f"  ❌ Error processing word '{word}': {e}")
        import traceback
        if debug:
            traceback.print_exc()
        return None


def load_german_base_data(level="A1", base_dir=None):
    """Load URLs and part of speech data from German JSON files"""
    if base_dir is None:
        base_dir = Path(__file__).parent / "app" / "german_base"
    else:
        base_dir = Path(base_dir)

    base_file = base_dir / f"{level}.json"

    try:
        with open(base_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Create mapping from word/lemma to pos and other data
        word_to_data = {}
        for item in data:
            # Use lemma field directly
            word = item.get('lemma')

            if word:
                word_to_data[word] = {
                    'pos': item.get('wortklasse', 'unknown'),
                    'url': item.get('url', ''),
                    'level': item.get('level', level)
                }

        return word_to_data
    except Exception as e:
        print(f"❌ Error loading {base_file}: {e}")
        return {}


def process_german_words(level="A1", max_words=None, output_dir=None, resume_from=0):
    """
    Process German words from base files and save in desired format.

    Args:
        level (str): Language level (A1, A2, B1, B2, C1, C2)
        max_words (int): Maximum number of words to process (None = all)
        output_dir (str): Output directory path (None = default app/german/)
        resume_from (int): Index to resume from (for continuing interrupted processing)

    Returns:
        list: List of processed word dictionaries
    """
    print(f"\n{'='*60}")
    print(f"Processing {level} Level German Vocabulary")
    print(f"Method: Web Scraping (for rich data)")
    print(f"{'='*60}\n")

    base_data = load_german_base_data(level)
    words = list(base_data.keys())
    print(f"📚 Found {len(words)} words in {level}.json")

    # Load existing data if resuming
    if output_dir is None:
        output_dir = Path(__file__).parent / "app" / "german"
    else:
        output_dir = Path(output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f"{level}.json"

    processed_words = []
    if resume_from > 0 and output_file.exists():
        print(f"📂 Loading existing data from {output_file}")
        with open(output_file, 'r', encoding='utf-8') as f:
            processed_words = json.load(f)
        print(f"✅ Loaded {len(processed_words)} existing words")

    # Determine range to process
    start_idx = resume_from if resume_from > 0 else 0
    end_idx = min(max_words, len(words)) if max_words else len(words)

    print(f"🔄 Processing words {start_idx + 1} to {end_idx} of {len(words)}")
    print(f"{'='*60}\n")

    failed_words = []

    for i, word in enumerate(words[start_idx:end_idx], start=start_idx):
        print(f"[{i+1}/{end_idx}] Processing: {word}")

        pos_data = base_data.get(word, {})
        result = extract_word_data_scraping(word, pos_data=pos_data, debug=False)

        if result:
            processed_words.append(result)
            print(f"  ✅ Successfully processed: {result['word']} ({result['partOfSpeech']})")
            if result.get('etymology'):
                print(f"     - Etymology: ✓")
            if result.get('compounds'):
                print(f"     - Compounds: {len(result['compounds'])} found")
            if result.get('examples'):
                print(f"     - Examples: {len(result['examples'])} found")
            if result.get('synonyms'):
                print(f"     - Synonyms: {len(result['synonyms'])} found")
            if result.get('frequency'):
                print(f"     - Frequency: {result['frequency']}")

            # Save progress every 10 words
            if (i + 1) % 10 == 0:
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(processed_words, f, indent=2, ensure_ascii=False)
                print(f"\n  💾 Progress saved ({len(processed_words)} words)\n")
        else:
            failed_words.append(word)
            print(f"  ❌ Failed to process: {word}")

        # Rate limiting to avoid overwhelming the server
        time.sleep(0.2)

    # Final save
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(processed_words, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*60}")
    print(f"✅ Processing Complete!")
    print(f"{'='*60}")
    print(f"📊 Total words processed: {len(processed_words)}")
    print(f"✅ Successful: {len(processed_words)}")
    print(f"❌ Failed: {len(failed_words)}")
    print(f"💾 Saved to: {output_file}")

    if failed_words:
        print(f"\n⚠️  Failed words:")
        for word in failed_words[:10]:  # Show first 10
            print(f"  - {word}")
        if len(failed_words) > 10:
            print(f"  ... and {len(failed_words) - 10} more")

    return processed_words


def download_lemma_database(output_file: str = "dwds_lemma_database.csv"):
    """
    Download the complete DWDS lemma database.

    Args:
        output_file: Output filename for the downloaded database

    Returns:
        bool: Success status
    """
    print(f"\n{'='*60}")
    print("Downloading DWDS Lemma Database")
    print(f"{'='*60}\n")

    try:
        # The lemma list page provides download links
        url = "https://www.dwds.de/lemma/list"
        print(f"📥 Fetching lemma database from {url}")

        response = requests.get(url, timeout=30)
        response.raise_for_status()

        # Save the downloaded file
        output_path = Path(__file__).parent / output_file
        with open(output_path, 'wb') as f:
            f.write(response.content)

        print(f"✅ Successfully downloaded lemma database to {output_path}")
        return True

    except Exception as e:
        print(f"❌ Error downloading lemma database: {e}")
        return False


def main():
    """Main entry point for the script"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Extract German vocabulary data from DWDS using web scraping',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process all A1 words
  python extract_dwds_data.py --level A1

  # Process first 100 B1 words
  python extract_dwds_data.py --level B1 --max-words 100

  # Resume processing from word 50
  python extract_dwds_data.py --level A2 --resume-from 50

  # Process all levels (A1 through C2)
  python extract_dwds_data.py --all-levels

  # Download DWDS lemma database
  python extract_dwds_data.py --download-lemma-db
        """
    )

    parser.add_argument('--level', type=str, default='A1',
                       choices=['A1', 'A2', 'B1', 'B2', 'C1', 'C2'],
                       help='Language level to process (default: A1)')
    parser.add_argument('--max-words', type=int, default=None,
                       help='Maximum number of words to process (default: all)')
    parser.add_argument('--resume-from', type=int, default=0,
                       help='Index to resume from (default: 0)')
    parser.add_argument('--all-levels', action='store_true',
                       help='Process all levels (A1 through C2)')
    parser.add_argument('--output-dir', type=str, default=None,
                       help='Output directory (default: app/german/)')
    parser.add_argument('--download-lemma-db', action='store_true',
                       help='Download the DWDS lemma database')

    args = parser.parse_args()

    if args.download_lemma_db:
        download_lemma_database()
    elif args.all_levels:
        levels = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']
        for level in levels:
            try:
                process_german_words(
                    level=level,
                    max_words=args.max_words,
                    output_dir=args.output_dir,
                    resume_from=0
                )
            except Exception as e:
                print(f"\n❌ Error processing {level}: {e}")
                continue
    else:
        process_german_words(
            level=args.level,
            max_words=args.max_words,
            output_dir=args.output_dir,
            resume_from=args.resume_from
        )


if __name__ == "__main__":
    main()
