from pathlib import Path
from unittest.mock import patch

from tools.pipeline.transcribe.transcriber import transcribe_audio


def test_transcribe_returns_segments(tmp_path):
    audio_file = tmp_path / "test.mp3"
    audio_file.touch()

    mock_segments = [
        {"start": 0.0, "end": 5.0, "text": "Hello world."},
        {"start": 5.0, "end": 10.0, "text": "How are you."},
    ]
    mock_result = {
        "text": "Hello world. How are you.",
        "segments": mock_segments,
        "language": "en",
    }

    with patch("pipeline.transcribe.transcriber.mlx_whisper") as mock_mlx:
        mock_mlx.transcribe.return_value = mock_result
        segments = transcribe_audio(audio_file)

    assert segments == mock_segments
    mock_mlx.transcribe.assert_called_once_with(
        str(audio_file),
        path_or_hf_repo="mlx-community/whisper-large-v3-mlx",
        word_timestamps=True,
        language="en",
    )


def test_transcribe_custom_model(tmp_path):
    audio_file = tmp_path / "test.mp3"
    audio_file.touch()

    mock_result = {"text": "", "segments": [], "language": "en"}

    with patch("pipeline.transcribe.transcriber.mlx_whisper") as mock_mlx:
        mock_mlx.transcribe.return_value = mock_result
        transcribe_audio(audio_file, model="custom-model")

    mock_mlx.transcribe.assert_called_once_with(
        str(audio_file),
        path_or_hf_repo="custom-model",
        word_timestamps=True,
        language="en",
    )
