# Maintainer notes

This directory holds the pipeline that produces the `wiki/` and `raw/sermons/` content. **You should only need any of this if you are rebuilding the wiki from scratch or pulling new sermons.** Everyone else should ignore `tools/` and just use the wiki.

## Pipeline overview

| Stage | Module | Command (run from repo root) |
|---|---|---|
| Download sermon audio + metadata | `tools/pipeline/download/` | `python -m tools.pipeline.download` |
| Transcribe MP3 → text (mlx-whisper) | `tools/pipeline/transcribe/` | `python -m tools.pipeline.transcribe` |
| Extract scripture references | `tools/pipeline/add_scripture_refs.py` | `python -m tools.pipeline.add_scripture_refs` |
| Compile wiki | [llm-wiki-compiler](https://github.com/anthropics/llm-wiki-compiler) | `/wiki-compile` (slash command in Claude Code) |

## Setup

Apple Silicon required for the transcriber (uses [mlx-whisper](https://github.com/ml-explore/mlx-whisper)).

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r tools/pipeline/download/requirements.txt
pip install -r tools/pipeline/transcribe/requirements.txt
```

## Step 1 — Download sermons

```bash
python -m tools.pipeline.download --limit 5 --verbose
```

Each sermon lands in `raw/sermons/<folder>/` with an MP3 and an `about.md`.

| Flag | Default | Description |
|---|---|---|
| `--limit N` | `5` | Max sermons per run. `0` = no limit. |
| `--retry-failed` | off | Reset failed entries to pending. |
| `--dry-run` | off | Discover and plan, don't download. |
| `--verbose` | off | Log each step. |

Hourly cron:

```cron
0 * * * * cd /Users/chris/git/tim-keller-bot && .venv/bin/python -m tools.pipeline.download --limit 5 >> /tmp/keller-download.log 2>&1
```

## Step 2 — Transcribe sermons

```bash
python -m tools.pipeline.transcribe
```

Walks `raw/sermons/`, writes a `.txt` next to each MP3 that doesn't have one yet.

| Flag | Description |
|---|---|
| `--sermon <name>` | Transcribe a single sermon by folder name. |
| `--force` | Re-transcribe even if a `.txt` exists. |
| `--verbose` | Show segment count and detailed progress. |

## Step 3 — Extract scripture references

```bash
python -m tools.pipeline.add_scripture_refs
```

Backfills `Scripture Reference` fields in `raw/sermons/*/about.md` by parsing the transcript.

## Step 4 — Compile wiki

In Claude Code:

```
/wiki-compile
```

Configuration is in `.wiki-compiler.json` at the repo root. Output goes to `wiki/`.

## Tests

```bash
source .venv/bin/activate
python -m pytest tools/ -c tools/pytest.ini
```

Tests that import `mlx_whisper` are skipped if it's not installed. Live network tests are opt-in:

```bash
python -m pytest tools/ -c tools/pytest.ini -m network
```

## One-off scripts

- `tools/repair_sermons.py` — manual transcript repair helper. Used during initial corpus cleanup; kept for reference.
