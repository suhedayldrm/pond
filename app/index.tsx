import React, { useEffect, useRef, useState } from 'react';
import {
  ActivityIndicator,
  ScrollView,
  StatusBar,
  StyleSheet,
  Text,
  TextInput,
  TouchableOpacity,
  View
} from 'react-native';

// Import all vocabulary levels
import A1Vocabulary from './german/A1.json';
import A2Vocabulary from './german/A2.json';
import B1Vocabulary from './german/B1.json';
import B2Vocabulary from './german/B2.json';

// Define the vocabulary word type
interface VocabWord {
  word: string;
  partOfSpeech: string;
  english: string;
  composition: string[];
  decompositionMeaning: string[];
  frequency: string | number | null;
  connected_words: Array<{ german: string; english: string }>;
  examples: Array<{ german: string; english: string }>;
  source_url: string;
  etymology?: { german: string; english: string };
  compounds?: Array<{ german: string; english: string }>;
}

type GameState = 'levelSelect' | 'playing' | 'gameOver';
type Level = 'A1' | 'A2' | 'B1' | 'B2';

const DEFAULT_FREQUENCY_TOTAL = 7;

const GermanVocabGame = () => {
  const [gameState, setGameState] = useState<GameState>('levelSelect');
  const [currentWord, setCurrentWord] = useState<VocabWord | null>(null);
  const [userAnswer, setUserAnswer] = useState('');
  const [score, setScore] = useState(0);
  const [timeLeft, setTimeLeft] = useState(180);
  const [feedback, setFeedback] = useState('');
  const [showEnhancedInfo, setShowEnhancedInfo] = useState(false);
  const [usedWords, setUsedWords] = useState<string[]>([]);
  const [selectedLevel, setSelectedLevel] = useState<Level | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const inputRef = useRef<TextInput>(null);
  const [awaitNext, setAwaitNext] = useState(false);
  const [isPaused, setIsPaused] = useState(false);

  // Get words based on selected level
  const getWords = (level: Level | null): VocabWord[] => {
    switch(level) {
      case 'A1': return Array.isArray(A1Vocabulary) ? A1Vocabulary : [];
      case 'A2': return Array.isArray(A2Vocabulary) ? A2Vocabulary : [];
      case 'B1': return Array.isArray(B1Vocabulary) ? B1Vocabulary : [];
      case 'B2': return Array.isArray(B2Vocabulary) ? B2Vocabulary : [];
      default: return [];
    }
  };

  const getRandomWord = (words: VocabWord[]): VocabWord | null => {
    if (!words || words.length === 0) return null;

    const availableWords = words.filter(word => !usedWords.includes(word.word));

    if (availableWords.length === 0) {
      setUsedWords([]);
      return words[Math.floor(Math.random() * words.length)];
    }

    return availableWords[Math.floor(Math.random() * availableWords.length)];
  };

  const parseFrequency = (value: VocabWord['frequency']) => {
    if (value === null || value === undefined) return null;

    if (typeof value === 'number') {
      return {
        active: Math.max(0, Math.min(value, DEFAULT_FREQUENCY_TOTAL)),
        total: DEFAULT_FREQUENCY_TOTAL
      };
    }

    const match = value.match(/(\d+)\s*(?:out of|of|\/)\s*(\d+)/i);
    if (!match) return null;

    const active = Number(match[1]);
    const total = Number(match[2]);
    if (!Number.isFinite(active) || !Number.isFinite(total) || total <= 0) return null;

    return {
      active: Math.max(0, Math.min(active, total)),
      total
    };
  };

  const startGame = async (level: Level) => {
    try {
      setIsLoading(true);
      setSelectedLevel(level);
      setScore(0);
      setTimeLeft(180);
      setUserAnswer('');
      setFeedback('');
      setShowEnhancedInfo(false);
      setUsedWords([]);
      
      const levelWords = getWords(level);
      const firstWord = getRandomWord(levelWords);
      
      if (!firstWord) {
        console.error('No words found for level:', level);
        return;
      }

      setCurrentWord(firstWord);
      setGameState('playing');
    } catch (error) {
      console.error('Error starting game:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const checkAnswer = () => {
    if (!currentWord || !userAnswer.trim()) return;

    const isCorrect = userAnswer.toLowerCase().trim() === currentWord.english.toLowerCase();

    setFeedback(isCorrect ? '✓ Correct!' : `✗ ${currentWord.word} = ${currentWord.english}`);

    if (isCorrect) {
      setScore(prev => prev + 10);
    }

    setShowEnhancedInfo(true);
    setAwaitNext(true);
    setIsPaused(true);
  };

  const nextWord = () => {
    const levelWords = getWords(selectedLevel);
    const nextWord = getRandomWord(levelWords);

    setCurrentWord(nextWord);
    setUserAnswer('');
    setFeedback('');
    setShowEnhancedInfo(false);
    setAwaitNext(false);
    setIsPaused(false);
    if (currentWord) {
      setUsedWords(prev => [...prev, currentWord.word]);
    }

    if (inputRef.current) inputRef.current.focus();
  };

  useEffect(() => {
    let timer;
    if (gameState === 'playing' && timeLeft > 0 && !isPaused) {
      timer = setTimeout(() => setTimeLeft(prev => prev - 1), 1000);
    } else if (timeLeft === 0) {
      setGameState('gameOver');
    }
    return () => clearTimeout(timer);
  }, [gameState, timeLeft, isPaused]);

  useEffect(() => {
    if (gameState === 'playing' && inputRef.current) {
      inputRef.current.focus();
    }
  }, [gameState, currentWord]);

  if (gameState === 'levelSelect') {
    return (
      <View style={styles.container}>
        <StatusBar barStyle="dark-content" backgroundColor="#f0f9ff" />
        <ScrollView contentContainerStyle={styles.scrollContainer}>
          <View style={styles.menuContainer}>
            <View style={styles.titleContainer}>
              <Text style={styles.title}>German Vocab</Text>
              <Text style={styles.subtitle}>Select Your Level</Text>
            </View>

            <View style={styles.instructionsContainer}>
              <Text style={styles.instructionsTitle}>How to play:</Text>
              <Text style={styles.instructionItem}>• Translate German to English</Text>
              <Text style={styles.instructionItem}>• 3 minutes timer</Text>
              <Text style={styles.instructionItem}>• Type and press Submit</Text>
            </View>

            <View style={styles.levelButtonsContainer}>
              <TouchableOpacity 
                style={[styles.levelButton, styles.a1Button]}
                onPress={() => startGame('A1')}
                disabled={isLoading}
              >
                {isLoading && selectedLevel === 'A1' ? (
                  <ActivityIndicator color="#fff" />
                ) : (
                  <Text style={styles.levelButtonText}>A1 (Beginner)</Text>
                )}
              </TouchableOpacity>

              <TouchableOpacity 
                style={[styles.levelButton, styles.a2Button]}
                onPress={() => startGame('A2')}
                disabled={isLoading}
              >
                {isLoading && selectedLevel === 'A2' ? (
                  <ActivityIndicator color="#fff" />
                ) : (
                  <Text style={styles.levelButtonText}>A2 (Elementary)</Text>
                )}
              </TouchableOpacity>

              <TouchableOpacity 
                style={[styles.levelButton, styles.b1Button]}
                onPress={() => startGame('B1')}
                disabled={isLoading}
              >
                {isLoading && selectedLevel === 'B1' ? (
                  <ActivityIndicator color="#fff" />
                ) : (
                  <Text style={styles.levelButtonText}>B1 (Intermediate)</Text>
                )}
              </TouchableOpacity>

              <TouchableOpacity 
                style={[styles.levelButton, styles.b2Button]}
                onPress={() => startGame('B2')}
                disabled={isLoading}
              >
                {isLoading && selectedLevel === 'B2' ? (
                  <ActivityIndicator color="#fff" />
                ) : (
                  <Text style={styles.levelButtonText}>B2 (Upper Intermediate)</Text>
                )}
              </TouchableOpacity>
            </View>
          </View>
        </ScrollView>
      </View>
    );
  }

  if (gameState === 'gameOver') {
    return (
      <View style={styles.container}>
        <StatusBar barStyle="dark-content" backgroundColor="#faf5ff" />
        <ScrollView contentContainerStyle={styles.scrollContainer}>
          <View style={styles.gameOverContainer}>
            <Text style={styles.gameOverTitle}>Game Over!</Text>
            
            <View style={styles.scoreContainer}>
              <Text style={styles.finalScore}>{score}</Text>
              <Text style={styles.scoreLabel}>Final Score</Text>
            </View>

            <TouchableOpacity
              style={styles.playAgainButton}
              onPress={() => setGameState('levelSelect')}
            >
              <Text style={styles.playAgainButtonText}>Select Level</Text>
            </TouchableOpacity>
          </View>
        </ScrollView>
      </View>
    );
  }

  if (gameState === 'playing') {
    if (!currentWord) {
      return (
        <View style={styles.container}>
          <ActivityIndicator size="large" color="#3b82f6" />
          <Text style={styles.loadingText}>Loading vocabulary...</Text>
        </View>
      );
    }

    const frequencyInfo = parseFrequency(currentWord?.frequency);

    return (
      <View style={styles.container}>
        <StatusBar barStyle="dark-content" backgroundColor="#f0fdf4" />
        <ScrollView contentContainerStyle={styles.scrollContainer}>
          <View style={styles.gameContainer}>
            <View style={styles.headerContainer}>
              <View style={styles.timerContainer}>
                <Text style={styles.timerText}>⏱️ {timeLeft}s</Text>
              </View>
              <View style={styles.scoreDisplayContainer}>
                <Text style={styles.scoreDisplay}>{score}</Text>
              </View>
            </View>

            <View style={styles.wordContainer}>
              <Text style={styles.turkishWord}>{currentWord?.word}</Text>
              <Text style={styles.translateText}>Translate to English</Text>

              {frequencyInfo && (
                <View style={styles.frequencyContainer}>
                  <Text style={styles.frequencyTitle}>Word frequency</Text>
                  <View style={styles.frequencyLabelRow}>
                    <Text style={styles.frequencyLabel}>rarely</Text>
                    <Text style={styles.frequencyLabel}>frequently</Text>
                  </View>
                  <View style={styles.frequencyBarRow}>
                    {Array.from(
                      { length: frequencyInfo.total },
                      (_, index) => {
                        const isActive = index < frequencyInfo.active;
                        return (
                          <View
                            key={`freq-${index}`}
                            style={[
                              styles.frequencyBar,
                              isActive
                                ? styles.frequencyBarActive
                                : styles.frequencyBarInactive
                            ]}
                          />
                        );
                      }
                    )}
                  </View>
                </View>
              )}

              {currentWord?.examples && currentWord.examples.length > 0 && (
                <View style={styles.exampleContainer}>
                  <Text style={styles.exampleLabel}>Example:</Text>
                  <Text style={styles.exampleText}>"{currentWord.examples[0].german}"</Text>
                </View>
              )}
            </View>

            <View style={styles.inputContainer}>
              <TextInput
                ref={inputRef}
                style={styles.textInput}
                value={userAnswer}
                onChangeText={setUserAnswer}
                placeholder="Type your answer..."
                placeholderTextColor="#9ca3af"
                editable={!awaitNext}
                returnKeyType="done"
                onSubmitEditing={checkAnswer}
                autoCapitalize="none"
                autoCorrect={false}
              />
              <TouchableOpacity 
                style={styles.submitButton} 
                onPress={checkAnswer}
                disabled={awaitNext}
              >
                <Text style={styles.submitButtonText}>Submit</Text>
              </TouchableOpacity>
            </View>

            {feedback ? (
              <View style={[
                styles.feedbackContainer,
                feedback.includes('✓') ? styles.correctFeedback : styles.incorrectFeedback
              ]}>
                <Text style={[
                  styles.feedbackText,
                  feedback.includes('✓') ? styles.correctFeedbackText : styles.incorrectFeedbackText
                ]}>
                  {feedback}
                </Text>
              </View>
            ) : null}

            {showEnhancedInfo && currentWord && (
              <View style={styles.enhancedInfoContainer}>
                {currentWord.composition && currentWord.composition.length > 0 && (
                  <View style={styles.decompositionContainer}>
                    <Text style={styles.decompositionTitle}>Word Breakdown:</Text>
                    {currentWord.composition.map((part, index) => (
                      <View key={index} style={styles.decompositionItem}>
                        <Text style={styles.decompositionPart}>{part}</Text>
                        <Text style={styles.decompositionArrow}>→</Text>
                        <Text style={styles.decompositionMeaning}>
                          {currentWord.decompositionMeaning[index] || ''}
                        </Text>
                      </View>
                    ))}
                  </View>
                )}
                {currentWord.connected_words && currentWord.connected_words.length > 0 && (
                  <View style={styles.connectedWordsContainer}>
                    <Text style={styles.connectedWordsTitle}>Connected Words:</Text>
                    <View style={styles.connectedWordsList}>
                      {currentWord.connected_words.map((word, index) => (
                        <Text key={index} style={styles.connectedWord}>
                          {word.german} ({word.english})
                        </Text>
                      ))}
                    </View>
                  </View>
                )}
              </View>
            )}

            {awaitNext && (
              <TouchableOpacity
                style={[styles.submitButton, { marginTop: 16 }]}
                onPress={nextWord}
              >
                <Text style={styles.submitButtonText}>Next</Text>
              </TouchableOpacity>
            )}
          </View>
        </ScrollView>
      </View>
    );
  }

  return null;
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f0f9ff',
    justifyContent: 'center',
    alignItems: 'center',
  },
  scrollContainer: {
    flexGrow: 1,
    justifyContent: 'center',
    padding: 20,
  },
  menuContainer: {
    backgroundColor: '#ffffff',
    borderRadius: 12,
    padding: 32,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 5,
  },
  titleContainer: {
    alignItems: 'center',
    marginBottom: 24,
  },
  title: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#1e40af',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    color: '#2563eb',
  },
  instructionsContainer: {
    backgroundColor: '#f3f4f6',
    borderRadius: 12,
    padding: 16,
    marginBottom: 24,
  },
  instructionsTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#374151',
    marginBottom: 8,
  },
  instructionItem: {
    fontSize: 14,
    color: '#6b7280',
    marginBottom: 4,
  },
  levelButtonsContainer: {
    width: '100%',
  },
  levelButton: {
    borderRadius: 12,
    paddingVertical: 16,
    paddingHorizontal: 24,
    alignItems: 'center',
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  a1Button: {
    backgroundColor: '#4CAF50',
  },
  a2Button: {
    backgroundColor: '#2196F3',
  },
  b1Button: {
    backgroundColor: '#FF9800',
  },
  b2Button: {
    backgroundColor: '#F44336',
  },
  levelButtonText: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  loadingText: {
    marginTop: 16,
    color: '#374151',
  },
  gameContainer: {
    backgroundColor: '#f0fdf4',
    borderRadius: 12,
    padding: 24,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 5,
  },
  headerContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 24,
  },
  timerContainer: {
    alignItems: 'flex-start',
  },
  timerText: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1d4ed8',
  },
  scoreDisplayContainer: {
    alignItems: 'flex-end',
  },
  scoreDisplay: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#16a34a',
  },
  wordContainer: {
    backgroundColor: '#ffffff',
    borderRadius: 12,
    padding: 24,
    alignItems: 'center',
    marginBottom: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 4,
    elevation: 2,
  },
  turkishWord: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#374151',
    marginBottom: 8,
    textAlign: 'center',
  },
  translateText: {
    fontSize: 14,
    color: '#6b7280',
    marginBottom: 12,
  },
  exampleContainer: {
    backgroundColor: '#f9fafb',
    borderLeftWidth: 4,
    borderLeftColor: '#3b82f6',
    borderRadius: 8,
    padding: 12,
    marginTop: 12,
    width: '100%',
  },
  exampleLabel: {
    fontSize: 12,
    color: '#6b7280',
    marginBottom: 4,
  },
  exampleText: {
    fontSize: 14,
    fontStyle: 'italic',
    color: '#374151',
  },
  frequencyContainer: {
    width: '100%',
    marginBottom: 12,
  },
  frequencyTitle: {
    fontSize: 12,
    color: '#374151',
    fontWeight: '600',
    marginBottom: 6,
  },
  frequencyLabelRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 6,
  },
  frequencyLabel: {
    fontSize: 11,
    color: '#6b7280',
  },
  frequencyBarRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    gap: 6,
  },
  frequencyBar: {
    height: 10,
    flex: 1,
    borderRadius: 4,
  },
  frequencyBarActive: {
    backgroundColor: '#1d4ed8',
  },
  frequencyBarInactive: {
    backgroundColor: '#e5e7eb',
  },
  inputContainer: {
    flexDirection: 'row',
    marginBottom: 16,
    gap: 8,
  },
  textInput: {
    flex: 1,
    backgroundColor: '#ffffff',
    borderWidth: 2,
    borderColor: '#d1d5db',
    borderRadius: 12,
    paddingVertical: 16,
    paddingHorizontal: 16,
    fontSize: 16,
    color: '#374151',
  },
  submitButton: {
    backgroundColor: '#3b82f6',
    borderRadius: 12,
    paddingVertical: 16,
    paddingHorizontal: 20,
    justifyContent: 'center',
    alignItems: 'center',
  },
  submitButtonText: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: '600',
  },
  feedbackContainer: {
    borderRadius: 12,
    padding: 12,
    alignItems: 'center',
    borderWidth: 2,
  },
  correctFeedback: {
    backgroundColor: '#dcfce7',
    borderColor: '#16a34a',
  },
  incorrectFeedback: {
    backgroundColor: '#fef2f2',
    borderColor: '#dc2626',
  },
  feedbackText: {
    fontSize: 16,
    fontWeight: '600',
    textAlign: 'center',
  },
  correctFeedbackText: {
    color: '#15803d',
  },
  incorrectFeedbackText: {
    color: '#dc2626',
  },
  enhancedInfoContainer: {
    marginTop: 16,
  },
  decompositionContainer: {
    backgroundColor: '#dcfce7',
    borderLeftWidth: 4,
    borderLeftColor: '#16a34a',
    borderRadius: 8,
    padding: 12,
    marginBottom: 12,
  },
  decompositionTitle: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#15803d',
    marginBottom: 8,
  },
  decompositionItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 4,
    gap: 8,
  },
  decompositionPart: {
    backgroundColor: '#bbf7d0',
    color: '#15803d',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 4,
    fontSize: 12,
    fontFamily: 'monospace',
  },
  decompositionArrow: {
    fontSize: 12,
    color: '#6b7280',
  },
  decompositionMeaning: {
    fontSize: 12,
    color: '#374151',
    flex: 1,
  },
  connectedWordsContainer: {
    backgroundColor: '#dbeafe',
    borderLeftWidth: 4,
    borderLeftColor: '#3b82f6',
    borderRadius: 8,
    padding: 12,
  },
  connectedWordsTitle: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#1d4ed8',
    marginBottom: 8,
  },
  connectedWordsList: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
  },
  connectedWord: {
    backgroundColor: '#bfdbfe',
    color: '#1d4ed8',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 16,
    fontSize: 12,
    fontWeight: '500',
  },
  gameOverContainer: {
    backgroundColor: '#faf5ff',
    borderRadius: 12,
    padding: 32,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 5,
  },
  gameOverTitle: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#7c3aed',
    marginBottom: 16,
  },
  scoreContainer: {
    backgroundColor: '#ffffff',
    borderRadius: 12,
    padding: 16,
    alignItems: 'center',
    marginBottom: 24,
    minWidth: 120,
  },
  finalScore: {
    fontSize: 36,
    fontWeight: 'bold',
    color: '#7c3aed',
    marginBottom: 8,
  },
  scoreLabel: {
    fontSize: 16,
    color: '#6b7280',
  },
  playAgainButton: {
    backgroundColor: '#7c3aed',
    borderRadius: 12,
    paddingVertical: 12,
    paddingHorizontal: 24,
    alignItems: 'center',
  },
  playAgainButtonText: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: 'bold',
  },
});

export default function App() {
  return <GermanVocabGame />;
}
