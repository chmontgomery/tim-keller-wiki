# Tim Keller Sermons — A Wiki for LLMs

A topic-organized knowledge base compiled from ~1,550 of Tim Keller's sermons. Designed to be plugged into any LLM (Claude, ChatGPT, Copilot, etc.) so it can answer questions in Keller's voice, grounded in his actual preaching, and cite the specific sermons that informed each answer.

The wiki is the primary artifact in this repo. You don't need to run anything to use it — it's just markdown files.

## What's here

```
.
├── wiki/          ← the compiled knowledge base (start here)
│   ├── INDEX.md       — list of all topics + "also known as" synonyms
│   ├── topics/        — 19 topic articles (one per major theme Keller preached on)
│   ├── concepts/      — cross-cutting patterns that span multiple topics
│   └── schema.md      — what fields each topic article contains
├── raw/sermons/   ← full text of every sermon (1 folder per sermon, with about.md + transcript)
├── AGENTS.md      ← instructions for any LLM consuming this wiki
└── tools/         ← maintainer-only pipeline (download/transcribe/compile). Ignore unless you're rebuilding the wiki.
```

## Using the wiki with an LLM

Any LLM that can read local files will work. The `AGENTS.md` file at the repo root tells the LLM how to navigate — start there, then read the relevant topic article, then fall back to raw transcripts only when you need a specific quote.

### Claude Desktop

1. Install the [Filesystem MCP server](https://github.com/modelcontextprotocol/servers/tree/main/src/filesystem) and point it at this repo.
2. Drop `tim-keller-advisor.skill` (in this repo's root) into Claude Desktop's skills folder, or have Claude load it directly.
3. Ask: *"What would Keller say about anxiety at work?"* — Claude will read the wiki and answer in his voice with citations.

### Claude Code (CLI)

Just open this repo and ask. `AGENTS.md` and `CLAUDE.md` will be loaded automatically and tell Claude how to search.

### ChatGPT / Copilot / other LLMs

Two options:

- **Upload the wiki.** Zip `wiki/` and `AGENTS.md` and attach them to a conversation. Then ask the model to "read AGENTS.md first, then answer my question using the wiki."
- **Workspace-aware tools (Copilot, Cursor, Codex, etc.).** Open this folder as a workspace. The LLM will pick up `AGENTS.md` automatically.

### Example prompt

> Using the Tim Keller wiki in this repo (start with `AGENTS.md`), answer in Keller's voice and cite the sermons you draw from: **How would Keller counsel someone who feels their identity is wrapped up in their career?**

## Attribution

Sermon transcripts and metadata are sourced from [gospelinlife.com](https://gospelinlife.com). See `LICENSE` for the fair-use notice and contact for permissions questions.

## Maintainer notes

If you're not me and you just want to use the wiki, you can stop reading. The `tools/` directory contains the Python pipeline that downloads sermons, transcribes them with mlx-whisper, and feeds the transcripts into [llm-wiki-compiler](https://github.com/anthropics/llm-wiki-compiler) to produce the topic articles. See `tools/README.md` for the build steps.
