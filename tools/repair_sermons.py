#!/usr/bin/env python3
"""
Bulk sermon text repair script.
Applies repair rules to sermon transcripts:
1. Collapse catastrophic phrase loops
2. Collapse 2-7x partial repetition
3. Fix word stutters
4. Normalize whitespace
5. Handle non-Latin characters
"""

import re
import sys
from pathlib import Path
from typing import List, Tuple

def collapse_phrase_loops(text: str) -> str:
    """Collapse catastrophic phrase loops (exact same phrase repeated 2+ times)."""
    # Match 3+ consecutive identical sentences/phrases
    lines = text.split('\n')
    result = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.strip():
            # Check for repeated identical lines
            count = 1
            while i + count < len(lines) and lines[i + count].strip() == line.strip():
                count += 1
            # If we found 3+ identical lines, keep just one
            if count >= 3:
                result.append(line)
                i += count
            else:
                result.append(line)
                i += 1
        else:
            result.append(line)
            i += 1

    text = '\n'.join(result)

    # Also handle phrase loops within paragraphs (e.g., "it is it is it is")
    # Match word/phrase repeated 3+ times separated by spaces
    pattern = r'\b(\w+(?:\s+\w+)*?)\s+\1\s+\1(\s+\1)*\b'
    text = re.sub(pattern, r'\1', text, flags=re.IGNORECASE)

    return text

def collapse_partial_repetition(text: str) -> str:
    """Collapse 2-7x partial/near repetitions of phrases or sentences."""
    # This handles cases like "it is it's it is" or "you know you know you know"

    # Pattern: a word/phrase followed by similar words 2-7 times
    # e.g., "you know you know you know" -> "you know"
    pattern = r'\b(\w+)\s+\1(\s+\1){1,6}\b'
    text = re.sub(pattern, r'\1', text, flags=re.IGNORECASE)

    # Handle phrase repetitions: "that's that that's that"
    pattern = r"\b((?:that'?s?|which|what|where|when|how|why)\s+[a-z]+)\s+\1(\s+\1){1,5}\b"
    text = re.sub(pattern, r'\1', text, flags=re.IGNORECASE)

    # Handle multi-word phrase repetitions
    pattern = r"\b(\w+\s+\w+)\s+\1(\s+\1){1,5}\b"
    text = re.sub(pattern, r'\1', text, flags=re.IGNORECASE)

    return text

def fix_word_stutters(text: str) -> str:
    """Fix word stutters (e.g., 'b-b-but', 'an-an-and', 'I I', 'and and')."""
    # Handle hyphenated stutters: "b-b-but" -> "but"
    text = re.sub(r'\b(\w)\1+-(\w+)\b', r'\2', text)

    # Handle space-separated word stutters
    # "I I said" -> "I said"
    text = re.sub(r'\b(\w+)\s+\1\s+', r'\1 ', text)

    # "and and and" at word boundaries
    text = re.sub(r'\b(\w+)\s+\1(?=\s)', r'\1', text)

    return text

def normalize_whitespace(text: str) -> str:
    """Normalize whitespace: multiple spaces, tabs, weird spacing."""
    # Replace multiple spaces with single space
    text = re.sub(r'  +', ' ', text)

    # Replace tabs with spaces
    text = re.sub(r'\t+', ' ', text)

    # Normalize line endings (remove excess blank lines but preserve some structure)
    text = re.sub(r'\n\n\n+', '\n\n', text)

    # Fix spacing around punctuation
    text = re.sub(r'\s+([,.!?;:])', r'\1', text)

    # Ensure space after punctuation if followed by word
    text = re.sub(r'([.!?])\n(?=[A-Za-z])', r'\1\n\n', text)

    # Strip trailing whitespace from each line
    lines = text.split('\n')
    lines = [line.rstrip() for line in lines]
    text = '\n'.join(lines)

    # Strip leading/trailing whitespace from entire text
    text = text.strip()

    return text

def handle_non_latin(text: str) -> str:
    """Handle non-Latin characters: replace with ASCII equivalents or remove."""
    # Replace smart quotes with straight quotes
    text = text.replace('"', '"')  # Left double quotation mark
    text = text.replace('"', '"')  # Right double quotation mark
    text = text.replace(''', "'")  # Left single quotation mark
    text = text.replace(''', "'")  # Right single quotation mark
    text = text.replace('–', '-')  # En dash
    text = text.replace('—', '-')  # Em dash
    text = text.replace('…', '...')  # Ellipsis

    # Remove other non-ASCII characters that aren't common symbols
    # Keep basic punctuation and Latin letters
    text = re.sub(r'[^\x00-\x7F\n\r]', '', text)

    return text

def repair_sermon(text: str) -> str:
    """Apply all repair rules to a sermon transcript."""
    # Order matters: do phrase loops first, then stutters, then repetitions, then whitespace
    text = collapse_phrase_loops(text)
    text = fix_word_stutters(text)
    text = collapse_partial_repetition(text)
    text = handle_non_latin(text)
    text = normalize_whitespace(text)
    return text

def process_file(filepath: Path) -> Tuple[str, str]:
    """
    Process a single sermon file.
    Returns: (filename, status)
    """
    try:
        # Read the file
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Apply repairs
        repaired = repair_sermon(content)

        # Write back
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(repaired)

        return (filepath.name, 'done')
    except FileNotFoundError:
        return (str(filepath), 'error')
    except Exception as e:
        return (str(filepath), f'error: {str(e)}')

def main():
    """Process all sermon files provided as arguments."""
    if len(sys.argv) < 2:
        print("Usage: python repair_sermons.py <file1> <file2> ...", file=sys.stderr)
        sys.exit(1)

    files = sys.argv[1:]

    for file_arg in files:
        filepath = Path(file_arg)
        filename, status = process_file(filepath)
        print(f"{filename}: {status}")

if __name__ == '__main__':
    main()
