from typing import Dict, List

Segment = Dict

PARAGRAPH_GAP_SECONDS = 2.0


def assemble_text(
    segments: List[Segment],
    paragraph_gap: float = PARAGRAPH_GAP_SECONDS,
) -> str:
    """Assemble transcription segments into text with paragraph breaks."""
    if not segments:
        return ""

    parts: List[str] = []
    current_paragraph: List[str] = []

    def flush_paragraph():
        if current_paragraph:
            parts.append(" ".join(current_paragraph))
            current_paragraph.clear()

    for i, seg in enumerate(segments):
        if i > 0:
            gap = seg["start"] - segments[i - 1]["end"]
            if gap >= paragraph_gap:
                flush_paragraph()
                parts.append("")

        current_paragraph.append(seg["text"].strip())

    flush_paragraph()

    text = "\n".join(parts)
    return text.rstrip() + "\n"


def process_segments(segments: List[Segment]) -> str:
    """Assemble transcription segments into text."""
    if not segments:
        return ""
    return assemble_text(segments)
