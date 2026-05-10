from pathlib import Path
from unittest.mock import MagicMock

import pytest

from tools.pipeline.download.downloader import (
    download_sermon,
    DownloadError,
)


def _metadata(mp3_url="https://s3.amazonaws.com/rpc-sermons/My_Sermon.mp3"):
    return {
        "title": "My Sermon",
        "speaker": "Tim Keller",
        "date": "2020-01-01",
        "series": None,
        "topics": [],
        "duration": None,
        "scripture": None,
        "sku": None,
        "overview": "",
        "mp3_url": mp3_url,
        "source_url": "https://gospelinlife.com/sermon/my-sermon/",
    }


def _streaming_response(chunks: list[bytes], status: int = 200):
    resp = MagicMock()
    resp.status_code = status
    resp.raise_for_status = MagicMock()
    resp.iter_bytes.return_value = iter(chunks)
    resp.__enter__ = lambda self: self
    resp.__exit__ = lambda self, *a: None
    return resp


def _client_with_stream(response):
    client = MagicMock()
    client.stream.return_value = response
    return client


def test_download_writes_mp3_and_returns_folder(tmp_path):
    resp = _streaming_response([b"hello ", b"world"])
    client = _client_with_stream(resp)

    folder = download_sermon(client, _metadata(), sermons_dir=tmp_path)

    assert folder.name == "My_Sermon"
    mp3 = folder / "My_Sermon.mp3"
    assert mp3.exists()
    assert mp3.read_bytes() == b"hello world"


def test_download_removes_part_file_on_success(tmp_path):
    resp = _streaming_response([b"data"])
    client = _client_with_stream(resp)

    folder = download_sermon(client, _metadata(), sermons_dir=tmp_path)

    assert not (folder / "My_Sermon.mp3.part").exists()


def test_download_error_removes_part_and_raises(tmp_path):
    resp = MagicMock()
    resp.status_code = 500
    resp.raise_for_status.side_effect = RuntimeError("server error")
    resp.__enter__ = lambda self: self
    resp.__exit__ = lambda self, *a: None
    client = _client_with_stream(resp)

    with pytest.raises(DownloadError):
        download_sermon(client, _metadata(), sermons_dir=tmp_path)

    folder = tmp_path / "My_Sermon"
    assert not (folder / "My_Sermon.mp3.part").exists()
    assert not (folder / "My_Sermon.mp3").exists()


def test_download_chunk_failure_removes_part(tmp_path):
    def chunks_then_boom():
        yield b"first chunk"
        raise ConnectionError("boom")

    resp = MagicMock()
    resp.status_code = 200
    resp.raise_for_status = MagicMock()
    resp.iter_bytes.return_value = chunks_then_boom()
    resp.__enter__ = lambda self: self
    resp.__exit__ = lambda self, *a: None
    client = _client_with_stream(resp)

    with pytest.raises(DownloadError):
        download_sermon(client, _metadata(), sermons_dir=tmp_path)

    folder = tmp_path / "My_Sermon"
    assert not (folder / "My_Sermon.mp3.part").exists()
