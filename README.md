# German Vocabulary Learning App

A comprehensive German vocabulary learning mobile app built with React Native and Expo. This app provides an interactive quiz game to help users learn German vocabulary with rich linguistic data including etymology, word composition, example sentences, and related words.

## Features

- **Multiple Proficiency Levels**: Support for A1, A2, B1, B2, C1, and C2 levels
- **Rich Vocabulary Data**: Each word includes:
  - English translation
  - Part of speech
  - Word composition/decomposition (prefixes, roots, suffixes)
  - Etymology information (when available)
  - Frequency rating
  - Connected/related words
  - Real-world example sentences
  - Compound word information
- **Interactive Quiz Game**:
  - 3-minute timed challenges
  - Score tracking
  - Enhanced word information display
  - Progressive difficulty by level
- **Data Source**: All vocabulary data extracted from [DWDS](https://www.dwds.de) (Digitales Wörterbuch der deutschen Sprache), the most comprehensive German dictionary

## Project Structure

```
german-vocab-native/
├── app/
│   ├── index.tsx              # Main app component (quiz game)
│   ├── german/                # Enriched German vocabulary data
│   │   ├── A1.json           # Beginner level (~800 words)
│   │   ├── A2.json           # Elementary level (~650 words)
│   │   ├── B1.json           # Intermediate level (~1,100 words)
│   │   ├── B2.json           # Upper intermediate (to be completed)
│   │   ├── C1.json           # Advanced (to be completed)
│   │   └── C2.json           # Proficiency (to be completed)
│   └── german_base/           # Raw source URLs for extraction
│       ├── A1.json           # Source URLs and metadata
│       ├── A2.json
│       ├── B1.json
│       └── C1.json
├── components/                # Reusable UI components
├── constants/                 # App constants (colors, etc.)
├── extract_dwds_data.py      # Main data extraction script
├── package.json              # Dependencies
└── README.md                 # This file
```

## Data Extraction Pipeline

### Prerequisites

Python dependencies (for data extraction):
```bash
pip install -r requirements.txt
```

### Extracting Vocabulary Data

The `extract_dwds_data.py` script uses **DWDS official APIs** to extract vocabulary data. This new API-based approach is **2x faster** and more reliable than the previous web scraping method.

**See [API_EXTRACTION_GUIDE.md](API_EXTRACTION_GUIDE.md) for detailed information about the API-based extraction.**

#### Basic Usage

Extract all words for a specific level:
```bash
python extract_dwds_data.py --level A1
```

Extract with a limit (useful for testing):
```bash
python extract_dwds_data.py --level B1 --max-words 100
```

Resume from a specific index (if interrupted):
```bash
python extract_dwds_data.py --level A2 --resume-from 250
```

Extract all levels at once:
```bash
python extract_dwds_data.py --all-levels
```

Download the DWDS lemma database:
```bash
python extract_dwds_data.py --download-lemma-db
```

#### Command Line Options

- `--level`: Language level (A1, A2, B1, B2, C1, C2) - default: A1
- `--max-words`: Maximum number of words to process - default: all
- `--resume-from`: Index to resume from - default: 0
- `--all-levels`: Process all levels sequentially
- `--output-dir`: Custom output directory - default: app/german/
- `--download-lemma-db`: Download complete DWDS lemma database

#### Data Format

Each vocabulary entry is structured as:

```json
{
  "word": "Achtung, die",
  "partOfSpeech": "noun",
  "english": "attention",
  "composition": ["achten", "-ung"],
  "decompositionMeaning": [
    "root word: to pay attention",
    "suffix: action/process"
  ],
  "frequency": "4 out of 7",
  "connected_words": [
    {"german": "Menschenrecht", "english": "human rights"},
    {"german": "Souveränität", "english": "sovereignty"}
  ],
  "examples": [
    {
      "german": "Achtung! Stufen!",
      "english": "Attention! Steps!"
    }
  ],
  "etymology": {
    "german": "von althochdeutsch ahta...",
    "english": "from Old High German ahta..."
  },
  "compounds": [
    {"german": "Achtungsapplaus", "english": "respectful applause"}
  ],
  "source_url": "https://www.dwds.de/wb/Achtung"
}
```

### Features of the Extraction Script

1. **API-Based**: Uses official DWDS APIs for reliable data extraction
2. **Fast Performance**: 2x faster than web scraping (0.5s vs 1s per word)
3. **Robust Error Handling**: Retries failed translations and network requests
4. **Rate Limiting**: Prevents overwhelming the DWDS server
5. **Progress Saving**: Automatically saves progress every 10 words
6. **Resume Capability**: Can continue from where it left off if interrupted
7. **Comprehensive Data**: Extracts frequency, IPA pronunciation, and morphological analysis
8. **Translation**: Automatically translates all German text to English using Google Translate

## Mobile App Setup

### Prerequisites

- Node.js 16+
- npm or yarn
- Expo CLI: `npm install -g expo-cli`
- Expo Go app on your mobile device (or iOS Simulator/Android Emulator)

### Installation

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npx expo start
```

3. Scan the QR code with:
   - **iOS**: Camera app (opens in Expo Go)
   - **Android**: Expo Go app

### Building for Production

For iOS:
```bash
npx expo build:ios
```

For Android:
```bash
npx expo build:android
```

## Technology Stack

### Frontend
- **React Native**: Cross-platform mobile framework
- **Expo**: Development platform for React Native
- **TypeScript**: Type-safe JavaScript

### Data Extraction
- **Python 3.8+**: Scripting language
- **Requests**: HTTP library for API calls
- **deep-translator**: Google Translate API wrapper

### Data Source
- **DWDS APIs**: Official APIs from Digitales Wörterbuch der deutschen Sprache (https://www.dwds.de/d/api)
- **DWDS Lemma Database**: Licensed under Creative Commons BY-SA 4.0

## Development Roadmap

### Completed ✅
- [x] Basic app structure with quiz game
- [x] Level selection (A1-B2)
- [x] Timer and scoring system
- [x] API-based data extraction script (2x faster)
- [x] A1, A2, B1 vocabulary data (~2,500 words)
- [x] Enhanced word information display
- [x] IPA pronunciation support

### In Progress 🚧
- [ ] Complete B2, C1, C2 vocabulary extraction
- [ ] Add unit tests for data extraction
- [ ] Performance optimization for large datasets

### Planned 📋
- [ ] Add pronunciation audio support
- [ ] Implement spaced repetition algorithm
- [ ] User progress tracking and statistics
- [ ] Flashcard mode
- [ ] Offline mode support
- [ ] Dark mode theme
- [ ] Multiple quiz types (multiple choice, listening, etc.)
- [ ] Backend API for cloud sync

## Data Attribution

All vocabulary data is sourced from **DWDS (Digitales Wörterbuch der deutschen Sprache)**, available at https://www.dwds.de. DWDS is a comprehensive digital dictionary of the German language maintained by the Berlin-Brandenburg Academy of Sciences and Humanities.

## Contributing

Contributions are welcome! Areas where help is needed:

1. **Data Quality**: Review and improve extracted vocabulary data
2. **Feature Development**: Add new quiz modes or learning features
3. **UI/UX**: Improve the user interface and experience
4. **Testing**: Write tests for components and data extraction
5. **Documentation**: Improve or translate documentation

## License

This project is for educational purposes. The DWDS Lemma Database is licensed under **Creative Commons BY-SA 4.0**. Please respect the DWDS API terms of service.

## Support

For issues or questions:
1. Check existing issues in the repository
2. Create a new issue with detailed description
3. Include error messages and steps to reproduce

## Acknowledgments

- **DWDS** for providing comprehensive German language data
- **Expo** team for the excellent React Native development platform
- **Google Translate** for translation API support
