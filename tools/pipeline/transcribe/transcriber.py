from pathlib import Path
from typing import Any, Dict, List

import mlx_whisper

DEFAULT_MODEL = "mlx-community/whisper-large-v3-mlx"


def transcribe_audio(
    audio_path: Path,
    model: str = DEFAULT_MODEL,
) -> List[Dict[str, Any]]:
    """Transcribe an audio file using mlx-whisper.

    Returns a list of segments, each with 'start', 'end', and 'text' keys.
    Model weights are cached on disk by huggingface-hub after first download.
    """
    result = mlx_whisper.transcribe(
        str(audio_path),
        path_or_hf_repo=model,
        word_timestamps=True,
        language="en",
        condition_on_previous_text=False,
        hallucination_silence_threshold=2.0,
        compression_ratio_threshold=1.8,
    )
    return result["segments"]
