---
description: Clean pending transcripts using parallel Claude subagents under Max auth
---

Your job is to drain `raw/sermons/.llm_followup.json` by repairing each listed transcript with a parallel subagent. Do exactly the following steps and nothing more.

## Step 1 — Build the manifest

Run:

```bash
python -m tools.pipeline.transcribe.prep_followup
```

Parse the stdout as JSON. It is an array of objects, each with keys `sermon`, `txt_path`, and `flags`.

If the array is empty, print `nothing to clean up` and stop.

## Step 2 — Load the repair prompt

Read `tools/pipeline/transcribe/repair_prompt.md` with the Read tool. Call its full contents `REPAIR_PROMPT` for the rest of this command.

## Step 3 — Dispatch all subagents in a single message

In one message, make one Task tool call per manifest entry (in parallel). For each entry, use `subagent_type: general-purpose` and a prompt of the following exact form, substituting the manifest values:

```
You are a transcript repair subagent. Follow these instructions literally.

<REPAIR_PROMPT>
{full body of REPAIR_PROMPT goes here verbatim}
</REPAIR_PROMPT>

<FILE>{txt_path}</FILE>
<FLAGS>{JSON of the flags array}</FLAGS>

Instructions:
1. Use the Read tool to read the file at <FILE>.
2. Apply the repair rules in <REPAIR_PROMPT> to the file contents. If <FLAGS> is non-empty, treat each entry as a suspect location (line, char_start, char_end, reason) and examine those positions carefully per Artifact 5.
3. Use the Write tool to write the corrected transcript back to <FILE>. Preserve paragraph breaks exactly.
4. When the Write succeeds, reply with the single word: done
5. If anything fails (file missing, Write fails, you cannot produce a repaired output), reply with a single line starting with "error:" followed by a short reason. Do not retry.

Do not reply with anything else. No preamble, no summary, no explanation.
```

Dispatch all subagents in parallel in a single assistant message — one Task tool_use block per entry. Do not dispatch them sequentially.

## Step 4 — Process results

For each subagent:

- If its reply is exactly `done`, run: `python -m tools.pipeline.transcribe.mark_done <sermon>` (substituting the sermon name).
- Otherwise, record the sermon name and the error line for the summary. Leave the log entry in place.

## Step 5 — Summary

Print one line: `N cleaned, M failed` where N is the count of subagents that replied `done` and M is the count that did not. If M > 0, follow with a bulleted list of `- <sermon>: <error line>`.
