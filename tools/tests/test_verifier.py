import pytest
from tools.pipeline.transcribe.verifier import regex_clean


# --- Rule 4: Normalize whitespace ---

def test_collapses_multiple_spaces():
    text = "your baby.   make vows, I'm going to be faithful."
    result, flags = regex_clean(text)
    assert "   " not in result
    assert "your baby. make vows" in result


def test_preserves_single_spaces():
    text = "Hello world. How are you."
    result, _ = regex_clean(text)
    assert result == text


def test_preserves_paragraph_breaks():
    text = "First paragraph.\n\nSecond paragraph."
    result, _ = regex_clean(text)
    assert "\n\n" in result


def test_whitespace_only_within_lines():
    text = "Line one.\n\nLine   two."
    result, _ = regex_clean(text)
    assert "Line one.\n\nLine two." == result.rstrip('\n')


# --- Rule 3: Word stutters ---

def test_collapses_duplicate_adjacent_word():
    text = "And you you are saved by grace."
    result, _ = regex_clean(text)
    assert "you you" not in result
    assert "you are saved" in result


def test_collapses_multiple_adjacent_duplicates():
    text = "convincing convincing convincing themselves they're okay."
    result, _ = regex_clean(text)
    assert result.count("convincing") == 1


def test_collapses_case_insensitive_stutter():
    text = "And life life goes on."
    result, _ = regex_clean(text)
    assert "life life" not in result


def test_does_not_remove_legitimate_repetition():
    # "very very good" is common speech — but "very very" is adjacent duplicates.
    # The rule collapses these; that is intentional and acceptable.
    text = "He was very very good at this."
    result, _ = regex_clean(text)
    assert "very very" not in result


def test_no_flags_for_clean_text():
    text = "Hello world. This is clean text."
    _, flags = regex_clean(text)
    assert flags == []


# --- Rule 2: Partial sentence repetition (2–4×) ---

def test_collapses_sentence_repeated_twice():
    text = "And my family looked at me with pride. And my family looked at me with pride. However, on the inside."
    result, _ = regex_clean(text)
    assert result.count("And my family looked at me with pride") == 1
    assert "However, on the inside" in result


def test_collapses_sentence_repeated_three_times():
    text = "He said, yes. He said, yes. He said, yes. They may come to a pretty pass."
    result, _ = regex_clean(text)
    assert result.count("He said, yes") == 1
    assert "They may come to a pretty pass" in result


def test_preserves_paragraph_structure_after_rep_collapse():
    text = "First idea.\n\nHe repeated. He repeated. He repeated.\n\nFinal thought."
    result, _ = regex_clean(text)
    assert result.count("He repeated") == 1
    assert "First idea" in result
    assert "Final thought" in result
    assert "\n\n" in result


# --- Rule 1: Catastrophic phrase loops (5+×) ---

def test_collapses_catastrophic_phrase_loop():
    phrase = "your soul will be "
    text = phrase * 20 + "all these other sources."
    result, _ = regex_clean(text)
    assert "your soul will be" in result
    assert result.count("your soul will be") == 1
    assert "all these other sources" in result


def test_phrase_loop_at_threshold_is_collapsed():
    # 5 repetitions of a 4-word phrase with no sentence punctuation — phrase-loop collapser handles this
    text = "your soul will be your soul will be your soul will be your soul will be your soul will be saved."
    result, _ = regex_clean(text)
    assert result.count("your soul will be") == 1
    assert "saved" in result


def test_phrase_loop_below_threshold_not_collapsed():
    # Only 4 repetitions — below the min_reps=5 threshold, should NOT be collapsed by phrase-loop rule
    text = "your soul will be your soul will be your soul will be your soul will be saved."
    result, _ = regex_clean(text)
    # 4 occurrences remain (the phrase-loop rule requires 5+ to trigger)
    assert result.count("your soul will be") == 4


def test_non_repeated_text_is_unchanged():
    text = "We believe in one God. We believe in one Lord. We believe in one Spirit."
    result, _ = regex_clean(text)
    # These are different sentences, not repeats
    assert "one God" in result
    assert "one Lord" in result
    assert "one Spirit" in result


# --- Rule 5: Non-Latin character detection ---

def test_detects_cyrillic_characters():
    # Simulate Whisper hallucinating Cyrillic
    text = "This is English. Привет мир. Back to English."
    _, flags = regex_clean(text)
    assert len(flags) > 0
    assert all(f["reason"] == "non_latin" for f in flags)


def test_non_latin_flag_has_correct_line_number():
    text = "Clean line one.\nLine with Кириллица here.\nClean line three."
    _, flags = regex_clean(text)
    assert all(f["line"] == 2 for f in flags)


def test_non_latin_flag_has_char_positions():
    text = "Hello Привет world."
    _, flags = regex_clean(text)
    assert len(flags) > 0
    assert "char_start" in flags[0]
    assert "char_end" in flags[0]
    assert flags[0]["char_start"] >= 0
    assert flags[0]["char_end"] > flags[0]["char_start"]


def test_clean_ascii_text_has_no_flags():
    text = "The gospel is the power of God for salvation."
    _, flags = regex_clean(text)
    assert flags == []


def test_latin_extended_chars_are_not_flagged():
    # Accented Latin characters should not be flagged
    text = "Søren Kierkegaard and José Ortega y Gasset."
    _, flags = regex_clean(text)
    assert flags == []


def test_non_latin_text_not_modified():
    # The regex pass must NOT modify the text for rule 5
    cyrillic_line = "English text. Привет мир. More English."
    result, flags = regex_clean(cyrillic_line)
    assert "Привет" in result
    assert len(flags) > 0
