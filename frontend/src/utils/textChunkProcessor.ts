/**
 * Utility functions for processing text chunks from voice transcription
 * Handles proper spacing and concatenation of numbers, symbols, and words
 */

export interface TextChunk {
  content: string;
  isNewChunk?: boolean;
}

/**
 * Determines if a chunk should be concatenated without space
 * @param currentContent - The existing text content
 * @param newChunk - The new chunk to be added
 * @returns true if chunks should be concatenated without space
 */
export function shouldConcatenateWithoutSpace(currentContent: string, newChunk: string): boolean {
  const trimmedCurrent = currentContent.trim();
  const trimmedChunk = newChunk.trim();
  
  // If current content is empty, always add the chunk
  if (!trimmedCurrent) return false;
  
  // Get the last character of current content and first character of new chunk
  const lastChar = trimmedCurrent[trimmedCurrent.length - 1];
  const firstChar = trimmedChunk[0];
  
  // If the new chunk starts with a space, it's a new word, don't concatenate
  if (/^\s/.test(newChunk)) {
    return false;
  }
  
  // Numbers and decimal/thousand separators should be concatenated
  if (isNumericCharacter(lastChar) && isNumericCharacter(firstChar)) {
    return true;
  }
  
  // Decimal points and commas in numbers
  if (isNumericCharacter(lastChar) && (firstChar === '.' || firstChar === ',')) {
    return true;
  }
  
  if ((lastChar === '.' || lastChar === ',') && isNumericCharacter(firstChar)) {
    return true;
  }
  
  // Currency symbols
  if (lastChar === '$' && isNumericCharacter(firstChar)) {
    return true;
  }
  
  if (isNumericCharacter(lastChar) && firstChar === '$') {
    return true;
  }
  
  // Punctuation that should be attached to the previous word
  // But NOT Spanish question/exclamation marks at the beginning of sentences
  if (isPunctuation(firstChar) && !isWhitespace(lastChar) && 
      firstChar !== '¿' && firstChar !== '¡') {
    return true;
  }
  
  // Special case: Spanish question marks and exclamation marks should be attached to the next word
  if ((lastChar === '¿' || lastChar === '¡') && /[a-zA-Z]/.test(firstChar)) {
    return true;
  }
  
  // Special case: If current content ends with punctuation and new chunk starts with Spanish punctuation,
  // add a space between them
  if (isPunctuation(lastChar) && (firstChar === '¿' || firstChar === '¡')) {
    return false; // Don't concatenate, let the normal spacing logic handle it
  }
  
  // For word continuation: analyze the structure rather than just length
  if (!chunkStartsWithSpace(newChunk) && !currentContentEndsWithSpace(currentContent) && 
      /[a-zA-Z]/.test(lastChar) && /[a-zA-Z]/.test(firstChar)) {
    
    // Check if this looks like word continuation based on structure
    return isWordContinuation(trimmedCurrent, trimmedChunk);
  }
  
  return false;
}

/**
 * Checks if a character is numeric (digit, decimal point, or comma)
 */
function isNumericCharacter(char: string): boolean {
  return /[\d.,]/.test(char);
}

/**
 * Checks if a character is punctuation
 */
function isPunctuation(char: string): boolean {
  return /[.,!?;:()\-_'"`¿¡]/.test(char);
}

/**
 * Checks if a character is whitespace
 */
function isWhitespace(char: string): boolean {
  return /\s/.test(char);
}

/**
 * Checks if a character is a word character (letter, digit, or underscore)
 */
function isWordCharacter(char: string): boolean {
  return /\w/.test(char);
}

/**
 * Checks if a chunk starts with whitespace
 */
function chunkStartsWithSpace(chunk: string): boolean {
  return /^\s/.test(chunk);
}

/**
 * Checks if current content ends with whitespace
 */
function currentContentEndsWithSpace(content: string): boolean {
  return /\s$/.test(content);
}

/**
 * Checks if current content ends with a complete word (followed by space or punctuation)
 */
function currentContentEndsWithCompleteWord(content: string): boolean {
  const trimmed = content.trim();
  if (!trimmed) return false;
  
  // Check if the last character is followed by space or punctuation
  const lastChar = trimmed[trimmed.length - 1];
  return isWhitespace(lastChar) || isPunctuation(lastChar);
}

/**
 * Analyzes the structure to determine if a chunk is part of the same word
 * @param currentContent - The existing text content
 * @param newChunk - The new chunk to be added
 * @returns true if the chunk appears to be part of the same word
 */
function isWordContinuation(currentContent: string, newChunk: string): boolean {
  // Get the last word from current content
  const words = currentContent.split(/\s+/);
  const lastWord = words[words.length - 1];
  
  // If the last word is very short (1-3 chars), it's likely incomplete
  if (lastWord.length <= 3) {
    return true;
  }
  
  // If the new chunk is very short (1-3 chars), it's likely part of the same word
  if (newChunk.length <= 3) {
    return true;
  }
  
  // Check if the last word looks incomplete (ends with common word fragments)
  const incompleteWordPatterns = [
    /^[a-z]$/i,           // Single letter
    /^[a-z]{1,3}$/i,      // Very short word (1-3 letters)
  ];
  
  if (incompleteWordPatterns.some(pattern => pattern.test(lastWord))) {
    return true;
  }
  
  // Check if the new chunk looks like a word fragment
  const fragmentPatterns = [
    /^[a-z]{1,3}$/i,      // Very short fragment
  ];
  
  if (fragmentPatterns.some(pattern => pattern.test(newChunk))) {
    return true;
  }
  
  // If both the last word and new chunk are reasonably long,
  // they're likely separate words
  if (lastWord.length >= 3 && newChunk.length >= 3) {
    return false;
  }
  
  // Default to concatenation for short chunks
  return true;
}

/**
 * Checks if a chunk is a number or special case that should be treated as a separate word
 */
function isNumberOrSpecialCase(chunk: string): boolean {
  const trimmed = chunk.trim();
  
  // Check if it's a number
  if (/^\d+$/.test(trimmed)) {
    return true;
  }
  
  // Only certain punctuation should be separate (opening punctuation)
  if (/^[¿¡(]/.test(trimmed)) {
    return true;
  }
  
  return false;
}

/**
 * Processes a new text chunk and returns the properly formatted content
 * @param currentContent - The existing text content
 * @param newChunk - The new chunk to be added
 * @returns The processed content with proper spacing
 */
export function processTextChunk(currentContent: string, newChunk: string): string {
  const trimmedCurrent = currentContent.trim();
  const trimmedChunk = newChunk.trim();
  
  // If current content is empty, return the new chunk
  if (!trimmedCurrent) {
    return trimmedChunk;
  }
  
  // If new chunk is empty, return current content
  if (!trimmedChunk) {
    return trimmedCurrent;
  }
  
  // Check if the new chunk starts with a space
  const chunkStartsWithSpace = /^\s/.test(newChunk);
  
  if (chunkStartsWithSpace) {
    // New chunk starts with space = new word, concatenate as-is
    return currentContent + newChunk;
  } else {
    // New chunk doesn't start with space = continuation of current word
    // Check if it's a number that should be separate
    if (/^\d+$/.test(trimmedChunk)) {
      // Check if the previous word ends with a currency symbol or comma
      const lastChar = trimmedCurrent[trimmedCurrent.length - 1];
      if (/[$€£¥,]/.test(lastChar)) {
        // Currency symbol or comma followed by number, concatenate without space
        return currentContent + newChunk;
      } else {
        // Regular number, add space before it
        return currentContent + ' ' + newChunk;
      }
    } else if (/^[$€£¥]/.test(trimmedChunk)) {
      // Currency symbols should be attached to the previous word
      return currentContent + newChunk;
    } else if (/^[.,]/.test(trimmedChunk)) {
      // Decimal/thousand separators should be attached to the previous word
      return currentContent + newChunk;
    } else {
      // Word continuation, concatenate without space
      return currentContent + newChunk;
    }
  }
}

/**
 * Processes multiple text chunks in sequence
 * @param chunks - Array of text chunks to process
 * @returns The final processed text
 */
export function processTextChunks(chunks: string[]): string {
  return chunks.reduce((acc, chunk) => processTextChunk(acc, chunk), '');
}

/**
 * Smart text chunk processor that handles complex scenarios
 * @param currentContent - The existing text content
 * @param newChunk - The new chunk to be added
 * @returns Object with processed content and metadata
 */
export function smartProcessTextChunk(currentContent: string, newChunk: string): {
  content: string;
  wasConcatenated: boolean;
  chunkType: 'word' | 'number' | 'punctuation' | 'symbol' | 'mixed';
} {
  const trimmedChunk = newChunk.trim();
  
  // Determine chunk type
  let chunkType: 'word' | 'number' | 'punctuation' | 'symbol' | 'mixed' = 'word';
  
  if (/^\d+$/.test(trimmedChunk)) {
    chunkType = 'number';
  } else if (/^[.,!?;:()\-_'"`]+$/.test(trimmedChunk)) {
    chunkType = 'punctuation';
  } else if (/^[^\w\s]+$/.test(trimmedChunk)) {
    chunkType = 'symbol';
  } else if (/[\d]/.test(trimmedChunk) && /[^\d\s]/.test(trimmedChunk)) {
    chunkType = 'mixed';
  }
  
  const processedContent = processTextChunk(currentContent, newChunk);
  // Check if the chunk starts with space - if so, no concatenation occurred
  const chunkStartsWithSpace = /^\s/.test(newChunk);
  const wasConcatenated = !chunkStartsWithSpace && processedContent === currentContent + newChunk;
  
  return {
    content: processedContent,
    wasConcatenated,
    chunkType
  };
}
