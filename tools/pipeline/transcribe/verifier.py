import re
from pathlib import Path

# ---------------------------------------------------------------------------
# Rules 1 & 2: Collapse consecutive repeated sentences and phrase loops
# ---------------------------------------------------------------------------

def _collapse_sentence_reps(line: str) -> str:
    """Collapse sentences repeated 2+ times consecutively within a line."""
    sentences = re.split(r"(?<=[.!?]) +", line)
    result: list[str] = []
    i = 0
    while i < len(sentences):
        s = sentences[i]
        j = i + 1
        while j < len(sentences) and sentences[j].strip().lower() == s.strip().lower():
            j += 1
        result.append(s)
        i = j  # j == i+1 if no repeat, j > i+1 if repeats found (all skipped)
    return " ".join(result)


def _collapse_phrase_loops(line: str, min_words: int = 4, min_reps: int = 5) -> str:
    """Collapse word-level phrase loops (e.g. 'your soul will be' × 20)."""
    words = line.split()
    result: list[str] = []
    i = 0
    while i < len(words):
        found = False
        max_plen = min(51, len(words) - i + 1)
        for plen in range(min_words, max_plen):
            phrase = words[i : i + plen]
            count = 1
            while i + (count + 1) * plen <= len(words):
                if words[i + count * plen : i + (count + 1) * plen] == phrase:
                    count += 1
                else:
                    break
            if count >= min_reps:
                result.extend(phrase)
                i += count * plen
                found = True
                break
        if not found:
            result.append(words[i])
            i += 1
    return " ".join(result)


def _collapse_repetitions(text: str) -> str:
    """Apply sentence and phrase repetition collapse, preserving paragraph structure."""
    lines = text.split("\n")
    result_lines = []
    for line in lines:
        if not line.strip():
            result_lines.append(line)
            continue
        line = _collapse_sentence_reps(line)
        line = _collapse_phrase_loops(line)
        result_lines.append(line)
    return "\n".join(result_lines)


# ---------------------------------------------------------------------------
# Rule 4: Normalize whitespace
# ---------------------------------------------------------------------------

def _normalize_whitespace(text: str) -> str:
    lines = text.split("\n")
    return "\n".join(re.sub(r"[ \t]{2,}", " ", line) for line in lines)


# ---------------------------------------------------------------------------
# Rule 3: Collapse word stutters  (e.g. "you you" → "you")
# ---------------------------------------------------------------------------

_STUTTER_RE = re.compile(r"(?i)\b(\w+)( \1)+\b")


def _collapse_word_stutters(text: str) -> str:
    return _STUTTER_RE.sub(r"\1", text)


# ---------------------------------------------------------------------------
# Rule 5: Detect non-Latin characters (flag for LLM review, do not modify)
# ---------------------------------------------------------------------------

# Matches characters outside Basic Latin (U+0000–U+007F),
# Latin-1 Supplement (U+0080–U+00FF), Latin Extended-A/B (U+0100–U+024F),
# and Latin Extended Additional (U+1E00–U+1EFF).
_NON_LATIN_RE = re.compile("[^\u0000-\u024F\u1E00-\u1EFF]")


def _detect_non_latin(text: str) -> list[dict]:
    flags: list[dict] = []
    for line_num, line in enumerate(text.split("\n"), start=1):
        for m in _NON_LATIN_RE.finditer(line):
            flags.append(
                {
                    "line": line_num,
                    "char_start": m.start(),
                    "char_end": m.end(),
                    "reason": "non_latin",
                }
            )
    return flags


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def regex_clean(text: str) -> tuple[str, list[dict]]:
    """Apply regex cleanup rules. Returns (cleaned_text, flags).

    Rules 1–4 modify the text. Rule 5 detects non-Latin characters and
    records their locations as flags without modifying the text.
    flags is a list of {line, char_start, char_end, reason} dicts.
    """
    text = _collapse_repetitions(text)
    text = _normalize_whitespace(text)
    text = _collapse_word_stutters(text)
    flags = _detect_non_latin(text)
    return text, flags


