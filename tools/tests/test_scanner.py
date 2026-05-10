from pathlib import Path

from tools.pipeline.transcribe.scanner import find_untranscribed


def test_finds_mp3_without_transcript(tmp_path):
    sermon_dir = tmp_path / "My_Sermon"
    sermon_dir.mkdir()
    mp3 = sermon_dir / "My_Sermon.mp3"
    mp3.touch()

    result = find_untranscribed(tmp_path)
    assert result == [mp3]


def test_skips_mp3_with_existing_transcript(tmp_path):
    sermon_dir = tmp_path / "My_Sermon"
    sermon_dir.mkdir()
    (sermon_dir / "My_Sermon.mp3").touch()
    (sermon_dir / "My_Sermon.txt").touch()

    result = find_untranscribed(tmp_path)
    assert result == []


def test_force_includes_already_transcribed(tmp_path):
    sermon_dir = tmp_path / "My_Sermon"
    sermon_dir.mkdir()
    mp3 = sermon_dir / "My_Sermon.mp3"
    mp3.touch()
    (sermon_dir / "My_Sermon.txt").touch()

    result = find_untranscribed(tmp_path, force=True)
    assert result == [mp3]


def test_sermon_filter_limits_to_one_folder(tmp_path):
    for name in ["Sermon_A", "Sermon_B"]:
        d = tmp_path / name
        d.mkdir()
        (d / f"{name}.mp3").touch()

    result = find_untranscribed(tmp_path, sermon_filter="Sermon_A")
    assert len(result) == 1
    assert result[0].parent.name == "Sermon_A"


def test_returns_sorted_paths(tmp_path):
    for name in ["Zebra", "Alpha", "Middle"]:
        d = tmp_path / name
        d.mkdir()
        (d / f"{name}.mp3").touch()

    result = find_untranscribed(tmp_path)
    names = [p.parent.name for p in result]
    assert names == ["Alpha", "Middle", "Zebra"]


def test_empty_directory_returns_empty(tmp_path):
    result = find_untranscribed(tmp_path)
    assert result == []
