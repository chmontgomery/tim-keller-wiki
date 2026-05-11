# Claude instructions

When using this repo to answer questions about Tim Keller, follow `AGENTS.md` at the repo root. It contains the persona, search strategy, and citation format you should use.

In short: read `wiki/INDEX.md` first, then the matching topic article in `wiki/topics/`, then `wiki/concepts/` if the question crosses topics, and only fall back to `raw/sermons/` for specific quotes or details not in the wiki.

For questions about **how to preach, sermon craft, or sermon review** (not theological topics), route to `wiki/teaching-courses/INDEX.md` instead — that section is primary for preaching-method questions.

## Repo layout

- `wiki/` — compiled knowledge base. Read this before raw sources.
- `raw/sermons/` — full transcripts (`<name>.txt`) and metadata (`about.md`) for every sermon.
- `raw/teaching-courses/` — TGC lecture courses (e.g. *Preaching Christ in a Postmodern World*). Same per-lecture layout as sermons.
- `tools/` — maintainer-only build pipeline. Don't touch unless you're rebuilding the wiki. See `tools/README.md`.

## Maintainer pipeline

Only relevant when rebuilding. All commands are run from repo root and use the `tools.pipeline.*` module path:

```bash
python -m tools.pipeline.download
python -m tools.pipeline.transcribe
python -m tools.pipeline.transcribe_course
python -m tools.pipeline.add_scripture_refs
/wiki-compile
```

Tests:

```bash
source .venv/bin/activate
python -m pytest tools/ -c tools/pytest.ini
```
