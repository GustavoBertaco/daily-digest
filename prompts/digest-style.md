# Daily Digest — Style Guide

Single source of truth for digest formatting and tone. The digest-writer and
digest-editor agents must follow this exactly. Reference example: `digests/2026-06-10.md`.

## File

- Path: `digests/YYYY-MM-DD.md` — date taken from the `fetched_at` field of `data/latest_fetch.json` (UTC date).
- One file per day. Never overwrite an existing digest for a previous date.

## Frontmatter

```markdown
---
date: YYYY-MM-DD
tags: [digest]
---
```

## Staleness banner

Only when the caller flags the data as stale — placed immediately after the frontmatter:

```markdown
> [!warning] Stale data
> Generated from data fetched at {fetched_at} ({age}h old). The scheduled GitHub Actions fetch may have failed — check the Actions tab.
```

## Structure

```markdown
# Daily Digest — {Month D, YYYY}

---

# {emoji} {Area Name}

## {Source Name}

**[Item Title](url)**
2-3 sentence summary paragraph.
```

- Title: `# Daily Digest — June 10, 2026` (en dash, full month name, no leading zero on day).
- Areas appear in the same order as in `data/latest_fetch.json`, separated by `---` horizontal rules.
- Area heading: `# {emoji} {Area Name}` using the area's emoji from the JSON.
- Source heading: `## {Source Name}` — only for sources that have items.
- Item: bold linked title `**[Title](url)**` on its own line, then the summary paragraph directly below (no blank line between title and summary).
- Items keep the order they have in the JSON.

## Empty sources and areas

- Sources in an area that returned no items get one combined line at the top of the area section:
  `> ⚠️ {Source A}, {Source B} — no new items in window`
- An area with no sources configured: `> No sources configured.`
- An area whose sources all failed or returned nothing: just the ⚠️ line, no source headings.

## Summaries

- 2-3 sentences, derived ONLY from the item's `title` and `content_snippet` in the JSON. Never invent facts, numbers, or conclusions not present in the snippet.
- For `source_type: youtube`, the snippet is a transcript excerpt — summarize the video's thesis or main argument, not the transcript fragment literally.
- Lead with why it matters or what is novel; include concrete numbers from the snippet when available.
- Tone: factual, compressed, no hype, no editorializing, no "this article discusses…" filler.
- If a snippet is too thin to support 2 sentences, write 1 accurate sentence rather than padding.
