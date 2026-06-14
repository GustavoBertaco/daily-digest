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
{summary — format depends on the area's summary_style, see below}
```

- Title: `# Daily Digest — June 10, 2026` (en dash, full month name, no leading zero on day).
- Areas appear in the same order as in `data/latest_fetch.json`, separated by `---` horizontal rules.
- Area heading: `# {emoji} {Area Name}` using the area's emoji from the JSON.
- Source heading: `## {Source Name}` — only for sources that have items.
- Item: bold linked title `**[Title](url)**` on its own line, then the summary directly below (no blank line between title and summary).
- Items keep the order they have in the JSON.

## Empty sources and areas

- Sources in an area that returned no items get one combined line at the top of the area section:
  `> ⚠️ {Source A}, {Source B} — no new items in window`
- An area with no sources configured: `> No sources configured.`
- An area whose sources all failed or returned nothing: just the ⚠️ line, no source headings.

## Summary styles

Each area in `data/latest_fetch.json` carries a `summary_style` field
(`insight` or `brief`, defaulting to `insight`). It selects the summary format
for every item in that area.

Shared rules (both styles):

- Tone: factual, compressed, no hype, no editorializing, no "this article
  discusses…" filler. Lead with why it matters or what is novel.
- Grounding is absolute: never invent facts, numbers, names, or conclusions not
  present in the source. A thin source yields a shorter summary, never padding.

### `brief` (e.g. Providers Updates)

- 2-3 sentences, derived ONLY from the item's `title` and `content_snippet` in
  the JSON. Include concrete numbers from the snippet when available.
- Do **not** expand brief items into a framing paragraph or bullet list.

### `insight` (default — all analytical areas)

Written in the voice of an experienced practitioner in that area sharing what
actually matters. Structure, directly under the `**[Title](url)**` line:

1. A 1-2 sentence **framing paragraph**: the problem or question the piece
   targets. For `source_type: youtube`/`podcast`, this is the video/episode
   *thesis* instead of a problem.
2. **3-5 insight bullets**, each `- **Lead phrase.** explanation` — the
   takeaways a senior practitioner would pull out.
3. Optionally, a final bullet with the single most memorable metric/takeaway.

Grounding for `insight`:

- For `rss`/`website` items, the summary is drafted from the **full article**
  fetched live (see digest-writer), not just the JSON snippet. Every bullet's
  facts must come from that article. Bullets may *interpret* stated facts, but
  must never introduce numbers, names, or claims the source doesn't contain.
- For `youtube`/`podcast` items, ground in the captured transcript/snippet.
- If the article can't be fetched, fall back to a `brief`-style summary from the
  snippet rather than inventing bullets.

Worked example (`insight`, condensed):

```markdown
**[Building Uber's Multi-Cloud Secrets Management Platform](https://example.com/post)**
Uber had secrets sprawl at scale — 150,000+ secrets across 25 separate vaults run by different teams. With no single front door, the org could no longer answer the basic question: who has access to what?

- **The problem was sprawl, not encryption.** Storing a secret was never hard; losing track of access across the org is. Their first move was unglamorous: collapse 25 vaults into 6, owned by one team.
- **The metadata model is the whole game.** Every secret tagged with provider, deployment platform, and impact level — once modeled, rotation and scoping become queries instead of heroics.
- **Knowing when *not* to automate.** They auto-rotate 20,000 secrets/month but stopped short of automating everything, pivoting to secretless auth instead.
- **One number to remember:** scoping access cut secrets distributed to workloads by 90%. The biggest win was distributing far less in the first place.
```
