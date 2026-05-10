from tools.pipeline.download.about import render_about_md


def _full_metadata():
    return {
        "title": "Peace – Overcoming Anxiety",
        "speaker": "Tim Keller",
        "date": "February 18, 1990",
        "series": "Fruit of the Spirit",
        "topics": ["Fruit of the Spirit", "Anxiety"],
        "duration": "42:29",
        "scripture": "Philippians 4:4-9",
        "sku": "RS 208-04-MP3",
        "overview": "The sermon addresses peace.",
        "mp3_url": "https://s3.amazonaws.com/rpc-sermons/Peace_Overcoming_Anxiety.mp3",
        "source_url": "https://gospelinlife.com/sermon/peace/",
    }


def test_renders_metadata_table_and_overview():
    md = render_about_md(_full_metadata())
    assert "# Metadata" in md
    assert "| Sermon Name | Peace – Overcoming Anxiety |" in md
    assert "| Speaker | Tim Keller |" in md
    assert "| Date | February 18, 1990 |" in md
    assert "| Downloaded From | https://gospelinlife.com/sermon/peace/ |" in md
    assert "| Series | Fruit of the Spirit |" in md
    assert "| Topics | Fruit of the Spirit, Anxiety |" in md
    assert "| Duration | 42:29 |" in md
    assert "| Scripture | Philippians 4:4-9 |" in md
    assert "| SKU | RS 208-04-MP3 |" in md
    assert "# Overview" in md
    assert "The sermon addresses peace." in md


def test_missing_optional_fields_render_as_em_dash():
    meta = _full_metadata()
    meta["series"] = None
    meta["duration"] = None
    meta["scripture"] = None
    meta["sku"] = None
    meta["topics"] = []

    md = render_about_md(meta)
    assert "| Series | — |" in md
    assert "| Duration | — |" in md
    assert "| Scripture | — |" in md
    assert "| SKU | — |" in md
    assert "| Topics | — |" in md


def test_empty_overview_renders_em_dash():
    meta = _full_metadata()
    meta["overview"] = ""
    md = render_about_md(meta)
    assert "# Overview\n—" in md


def test_output_ends_with_single_newline():
    md = render_about_md(_full_metadata())
    assert md.endswith("\n")
    assert not md.endswith("\n\n\n")
