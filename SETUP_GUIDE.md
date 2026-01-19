# Setup Guide - German Vocabulary App

This guide will help you get started with extracting vocabulary data and running the German vocabulary learning app.

## Quick Start

### 1. Install Python Dependencies

First, install the required Python packages for data extraction:

```bash
pip3 install -r requirements.txt
```

Or install individually:
```bash
pip3 install beautifulsoup4 requests deep-translator
```

### 2. Extract Vocabulary Data (Optional)

If you want to extract fresh data or complete missing levels (B2, C1, C2):

**Test the extraction script with a small sample:**
```bash
python3 extract_dwds_data.py --level A1 --max-words 10
```

**Extract a complete level:**
```bash
# This will take time depending on the number of words
python3 extract_dwds_data.py --level B2
```

**Extract all levels (will take several hours):**
```bash
python3 extract_dwds_data.py --all-levels
```

**Resume interrupted extraction:**
```bash
# If extraction was interrupted at word 150
python3 extract_dwds_data.py --level B2 --resume-from 150
```

### 3. Run the Mobile App

Install Node.js dependencies:
```bash
npm install
```

Start the development server:
```bash
npx expo start
```

Then scan the QR code with:
- **iOS**: Camera app (will open in Expo Go)
- **Android**: Expo Go app

## Current Data Status

### Completed ✅
- **A1**: ~800 words extracted and enriched
- **A2**: ~650 words extracted and enriched
- **B1**: ~1,100 words extracted and enriched

### To Complete 🚧
- **B2**: Base URLs available, needs extraction (~500+ words expected)
- **C1**: Base URLs available, needs extraction (~200+ words expected)
- **C2**: Not yet available

## Data Extraction Details

### What Gets Extracted

For each German word, the script extracts:

1. **Basic Info**
   - German word with article (e.g., "Achtung, die")
   - Part of speech (noun, verb, adjective, etc.)
   - English translation

2. **Morphological Analysis**
   - Word composition (prefixes, roots, suffixes)
   - Meaning of each component

3. **Linguistic Context**
   - Etymology (origin and historical development)
   - Frequency rating (1-7 scale)
   - 3 example sentences with translations
   - 4 connected/related words with translations

4. **Compound Words**
   - Up to 5 compound words containing the word
   - Translations for each compound

5. **Metadata**
   - Source URL from DWDS
   - Part of speech in English

### Extraction Time Estimates

- **A1** (~800 words): 2-3 hours
- **A2** (~650 words): 1.5-2 hours
- **B1** (~1,100 words): 3-4 hours
- **B2** (~500 words): 1-2 hours
- **C1** (~200 words): 30-60 minutes

*Note: Times vary based on internet connection and DWDS server response times*

### Handling Errors

The extraction script has built-in error handling:

1. **Translation Failures**: Retries up to 3 times with exponential backoff
2. **Network Errors**: Logs error and continues to next word
3. **Progress Saving**: Saves every 10 words automatically
4. **Resume Support**: Can continue from any point using `--resume-from`

If extraction fails repeatedly:
- Check your internet connection
- Verify DWDS website is accessible
- Try reducing the rate by adding longer delays in the script

## App Features

### Current Features
- Level selection (A1-B2)
- 3-minute timed quiz
- Score tracking
- Enhanced word information display
- Word composition breakdown
- Connected words display

### Planned Features
- [ ] Pronunciation audio
- [ ] Spaced repetition algorithm
- [ ] Progress tracking
- [ ] Flashcard mode
- [ ] Dark mode
- [ ] Multiple quiz types

## Troubleshooting

### Python Issues

**ModuleNotFoundError: No module named 'deep_translator'**
```bash
pip3 install deep-translator
```

**SSL Certificate Error**
```bash
# On macOS, install certificates
/Applications/Python\ 3.x/Install\ Certificates.command
```

### App Issues

**Metro bundler error**
```bash
# Clear cache and restart
npx expo start --clear
```

**Module resolution errors**
```bash
# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install
```

**TypeScript errors**
```bash
# Run TypeScript check
npx tsc --noEmit
```

### Data Issues

**Empty or corrupted JSON files**
- Delete the corrupted file
- Re-run extraction for that level

**Missing data fields**
- Some words may not have all fields (etymology, compounds)
- This is normal - the app handles missing fields gracefully

## File Structure After Setup

```
german-vocab-native/
├── app/
│   ├── index.tsx              # Main app component
│   ├── german/                # Extracted vocabulary data
│   │   ├── A1.json           # ✅ Complete
│   │   ├── A2.json           # ✅ Complete
│   │   ├── B1.json           # ✅ Complete
│   │   ├── B2.json           # 🚧 To be completed
│   │   ├── C1.json           # 🚧 To be completed
│   │   └── C2.json           # ❌ Not available
│   └── german_base/           # Source URLs
│       ├── A1.json
│       ├── A2.json
│       ├── B1.json
│       └── C1.json
├── extract_dwds_data.py      # Data extraction script
├── requirements.txt           # Python dependencies
├── package.json              # Node dependencies
├── README.md                 # Project documentation
└── SETUP_GUIDE.md            # This file
```

## Next Steps

1. **Install dependencies** (Python and Node.js)
2. **Test extraction** with a small sample
3. **Run the app** to verify it works
4. **Extract missing levels** (B2, C1) if needed
5. **Customize the app** to your needs

## Contributing

If you improve the extraction script or add features:
1. Test thoroughly
2. Update documentation
3. Create clear commit messages
4. Consider sharing improvements

## Resources

- **DWDS Website**: https://www.dwds.de
- **Expo Documentation**: https://docs.expo.dev
- **React Native Docs**: https://reactnative.dev
- **Python Requests**: https://requests.readthedocs.io
- **BeautifulSoup**: https://www.crummy.com/software/BeautifulSoup/

## Support

For issues or questions:
1. Check this guide
2. Review the main README.md
3. Check the script's help: `python3 extract_dwds_data.py --help`
4. Open an issue in the repository

---

Happy learning! 🇩🇪📚
