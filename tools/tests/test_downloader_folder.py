import pytest

from tools.pipeline.download.downloader import FolderNameError, folder_name_from_mp3_url


def test_simple_mp3_url():
    url = "https://s3.amazonaws.com/rpc-sermons/Peace_Overcoming_Anxiety.mp3"
    assert folder_name_from_mp3_url(url) == "Peace_Overcoming_Anxiety"


def test_url_encoded_underscore():
    url = "https://s3.amazonaws.com/rpc-sermons/Peace%5FOvercoming%5FAnxiety.mp3"
    assert folder_name_from_mp3_url(url) == "Peace_Overcoming_Anxiety"


def test_url_with_query_string():
    url = "https://s3.amazonaws.com/rpc-sermons/Aspiration_Lead_Us.mp3?foo=bar"
    assert folder_name_from_mp3_url(url) == "Aspiration_Lead_Us"


def test_url_with_uppercase_extension():
    url = "https://s3.amazonaws.com/rpc-sermons/My_Sermon.MP3"
    assert folder_name_from_mp3_url(url) == "My_Sermon"


def test_url_with_no_mp3_extension_raises():
    with pytest.raises(FolderNameError):
        folder_name_from_mp3_url("https://example.com/some/page")


def test_url_with_dot_only_stem_raises():
    with pytest.raises(FolderNameError):
        folder_name_from_mp3_url("https://s3.amazonaws.com/rpc-sermons/.mp3")
