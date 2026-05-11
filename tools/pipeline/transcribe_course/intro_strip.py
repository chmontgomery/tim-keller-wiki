"""Strip the TGC announcer intro from a course lecture transcript.

Every Keller lecture in the "Preaching Christ in a Postmodern World" course
opens with a narrator who introduces the session and hands off with a
sentence like "Here now is Dr. Tim Keller." Everything before (and
including) that hand-off sentence is announcer speech, not Keller, and
should be removed.

If no hand-off marker is found, the text is returned unchanged and the
caller is told so via the `found` flag.
"""
from __future__ import annotations

import re

# Allow "Dr. Tim Keller", "Tim Keller", "Dr. Keller", optional trailing
# punctuation. Case-insensitive. The marker is a full sentence — we anchor
# on "Here now is" so we don't match incidental mentions later in the text.
_HANDOFF_RE = re.compile(
    r"\bHere now is\s+(?:Dr\.?\s+)?(?:Tim\s+)?Keller\.?",
    re.IGNORECASE,
)


def strip_intro(text: str) -> tuple[str, bool]:
    """Remove the announcer intro up to and including the hand-off sentence.

    Returns (stripped_text, found). When no marker matches, the original
    text is returned with found=False so the caller can flag it for review.
    """
    match = _HANDOFF_RE.search(text)
    if not match:
        return text, False
    remainder = text[match.end():].lstrip()
    if not remainder.endswith("\n"):
        remainder += "\n"
    return remainder, True
