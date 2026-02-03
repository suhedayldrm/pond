# German Vocab

A German vocabulary quiz app built with React Native and Expo. Translate German words to English within a 3-minute timer, with word breakdowns, pronunciation, and rich linguistic data sourced from DWDS.

## Features

- **CEFR levels A1 through C2** plus a mixed mode with all levels combined
- **12,800+ words** sourced from [DWDS](https://www.dwds.de) (Digitales Worterbuch der deutschen Sprache)
- **Word breakdown (Wortzerlegung)** showing prefix, root, and suffix meanings for compound words
- **Text-to-speech** pronunciation for each word (German TTS via expo-speech)
- **Word frequency indicator** showing how common each word is
- **Example sentences** with English translations
- **Synonyms and collocations** displayed after each answer
- **Timed gameplay** with scoring (3-minute rounds, 10 points per correct answer)

## Word Counts by Level

| Level | Words |
|-------|-------|
| A1 (Beginner) | 819 |
| A2 (Elementary) | 616 |
| B1 (Intermediate) | 2,497 |
| B2 (Upper Intermediate) | 2,986 |
| C1 (Advanced) | 2,972 |
| C2 (Mastery) | 2,962 |
| Mix (All Levels) | 12,852 |

## Tech Stack

- **React Native** 0.79 with Expo SDK 53
- **TypeScript**
- **Expo Router** for navigation
- **Expo Speech** for text-to-speech
- **EAS Build** for Android distribution

### Data Pipeline (Python)

- **Requests** + **BeautifulSoup** for DWDS scraping
- **deep-translator** for Google Translate
- **multiprocessing** / **ThreadPoolExecutor** for parallel extraction

## Getting Started

### Prerequisites

- Node.js
- Expo CLI (`npm install -g expo-cli`)
- Expo Go app on your mobile device (or an emulator)

### Install and Run

```bash
npm install
npx expo start
```

Scan the QR code with Expo Go (Android) or the Camera app (iOS).

### Build for Production

```bash
# Android AAB (Google Play)
eas build --platform android --profile production

# Android APK (direct install)
eas build --platform android --profile preview
```

## Project Structure

```
app/
  index.tsx              # Main game screen (level select, quiz, game over)
  german/                # Vocabulary JSON data
    A1.json - C2.json    # Per-level vocabulary
    mix.json             # All levels combined
  german_base/           # Raw CEFR word lists (source URLs)
extract_dwds_data.py     # Main DWDS scraping script
reextract_random.py      # Random word selection from base lists (B2/C1/C2)
update_wortzerlegung.py  # Batch update word composition from DWDS
add_translations.py      # Batch translate all fields via Google Translate
```

## Data Format

Each vocabulary entry:

```json
{
  "word": "Achtung",
  "partOfSpeech": "noun",
  "english": "attention",
  "composition": ["Acht-", "-ung"],
  "decompositionMeaning": ["root word: respect", "suffix: action/process"],
  "frequency": "4 out of 7",
  "connected_words": [
    { "german": "Beachtung", "english": "attention" }
  ],
  "synonyms": [
    { "german": "Vorsicht", "english": "caution" }
  ],
  "examples": [
    { "german": "Achtung! Stufen!", "english": "Attention! Steps!" }
  ],
  "source_url": "https://www.dwds.de/wb/Achtung"
}
```

## Data Extraction

```bash
# Extract words for a level
python extract_dwds_data.py --level A1

# Randomly select and scrape B2/C1/C2 words from base lists
python reextract_random.py

# Update Wortzerlegung for all levels
python update_wortzerlegung.py --all-levels

# Translate all fields to English
python add_translations.py --all-levels
```

## Data Attribution

All vocabulary data is sourced from **DWDS (Digitales Worterbuch der deutschen Sprache)** at https://www.dwds.de, maintained by the Berlin-Brandenburg Academy of Sciences and Humanities. The DWDS Lemma Database is licensed under **Creative Commons BY-SA 4.0**.
