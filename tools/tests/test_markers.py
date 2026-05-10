from tools.pipeline.transcribe.markers import assemble_text, process_segments


def _seg(start, end, text):
    """Helper to create a segment dict."""
    return {"start": start, "end": end, "text": text}


# --- Text assembly ---

def test_assemble_plain_text():
    segments = [
        _seg(0, 5, "Hello world."),
        _seg(5, 10, "How are you."),
    ]
    result = assemble_text(segments)
    assert "Hello world." in result
    assert "How are you." in result


def test_assemble_paragraph_break_on_gap():
    segments = [
        _seg(0, 5, "First sentence."),
        _seg(8, 13, "After a pause."),  # 3-second gap
    ]
    result = assemble_text(segments)
    assert "\n\n" in result


def test_assemble_no_break_on_small_gap():
    segments = [
        _seg(0, 5, "First."),
        _seg(5.5, 10, "Second."),  # 0.5-second gap
    ]
    result = assemble_text(segments)
    # Should be on same line, joined by space
    assert "First. Second." in result


def test_assemble_empty_segments():
    assert assemble_text([]) == ""


def test_process_segments_end_to_end():
    segments = [
        _seg(0, 30, "Let me read the scripture. Matthew chapter 6 verse 9."),
        _seg(30, 90, "Our Father who art in heaven, hallowed be thy name."),
        _seg(90, 100, "And this is God's word."),
        _seg(105, 600, "So tonight we will look at four things about prayer."),
    ]
    result = process_segments(segments)
    assert "Matthew chapter 6 verse 9" in result
    assert "So tonight we will look at four things about prayer" in result
