from unittest.mock import patch

from tools.pipeline.transcribe.__main__ import parse_args, main


def test_parse_args_defaults():
    args = parse_args([])
    assert args.sermon is None
    assert args.force is False
    assert args.verbose is False


def test_parse_args_all_flags():
    args = parse_args(["--sermon", "My_Sermon", "--force", "--verbose"])
    assert args.sermon == "My_Sermon"
    assert args.force is True
    assert args.verbose is True


def test_parse_args_rejects_followup_only():
    # --followup-only has been removed in favor of /cleanup-transcripts
    import pytest
    with pytest.raises(SystemExit):
        parse_args(["--followup-only"])


@patch("pipeline.transcribe.__main__.transcribe_audio")
@patch("pipeline.transcribe.__main__.find_untranscribed")
def test_main_skips_when_nothing_to_do(mock_find, mock_transcribe, tmp_path, capsys):
    mock_find.return_value = []
    with patch("pipeline.transcribe.__main__.SERMONS_DIR", tmp_path):
        main(["--sermon", "Nonexistent"])
    mock_transcribe.assert_not_called()
    captured = capsys.readouterr()
    assert "No sermons to transcribe" in captured.out


@patch("pipeline.transcribe.__main__.process_segments")
@patch("pipeline.transcribe.__main__.transcribe_audio")
@patch("pipeline.transcribe.__main__.find_untranscribed")
def test_main_transcribes_regex_cleans_and_logs(
    mock_find, mock_transcribe, mock_process, tmp_path
):
    mp3 = tmp_path / "Sermon_A" / "Sermon_A.mp3"
    mp3.parent.mkdir()
    mp3.touch()

    mock_find.return_value = [mp3]
    mock_transcribe.return_value = [{"start": 0, "end": 5, "text": "Hello"}]
    mock_process.return_value = "Hello\n"

    log_path = tmp_path / ".llm_followup.json"

    with patch("pipeline.transcribe.__main__.SERMONS_DIR", tmp_path):
        with patch("pipeline.transcribe.__main__.LOG_PATH", log_path):
            main([])

    txt = mp3.with_suffix(".txt")
    assert txt.exists()
    # regex_clean is real, not mocked; "Hello\n" is idempotent
    assert txt.read_text() == "Hello\n"

    # Every transcribed sermon must land in the followup log
    import json
    entries = json.loads(log_path.read_text())
    assert [e["sermon"] for e in entries] == ["Sermon_A"]


@patch("pipeline.transcribe.__main__.transcribe_audio")
@patch("pipeline.transcribe.__main__.find_untranscribed")
def test_main_continues_on_error(mock_find, mock_transcribe, tmp_path, capsys):
    mp3_a = tmp_path / "A" / "A.mp3"
    mp3_b = tmp_path / "B" / "B.mp3"
    mp3_a.parent.mkdir()
    mp3_b.parent.mkdir()
    mp3_a.touch()
    mp3_b.touch()

    mock_find.return_value = [mp3_a, mp3_b]
    mock_transcribe.side_effect = [RuntimeError("model failed"), [{"start": 0, "end": 5, "text": "OK"}]]

    log_path = tmp_path / ".llm_followup.json"

    with patch("pipeline.transcribe.__main__.process_segments", return_value="OK\n"):
        with patch("pipeline.transcribe.__main__.SERMONS_DIR", tmp_path):
            with patch("pipeline.transcribe.__main__.LOG_PATH", log_path):
                main([])

    captured = capsys.readouterr()
    assert "failed" in captured.out.lower() or "error" in captured.out.lower()
    assert mp3_b.with_suffix(".txt").exists()

    # Only the successful sermon is in the log
    import json
    entries = json.loads(log_path.read_text())
    assert [e["sermon"] for e in entries] == ["B"]
