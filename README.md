# daily-digest

Automated daily digest aggregator. A scheduled remote Claude agent fetches content from RSS feeds, YouTube channels, podcasts, and websites — then writes concise Obsidian-compatible `.md` summaries organized by knowledge area.

## How it works

1. **GitHub Actions** (`.github/workflows/fetch.yml`, 9:45 UTC daily) runs `src/fetch.py`, committing `data/latest_fetch.json`, the seen-URL registry, and a run log
2. A **Claude cloud routine** runs daily at **7:00 AM São Paulo (10:00 UTC)** — its prompt is versioned at `prompts/daily-routine.md`:
   - checks data freshness (`src/check_freshness.py`); if the Actions fetch failed it re-fetches, or flags the digest with a staleness banner
   - the **digest-writer** subagent (`.claude/agents/digest-writer.md`) drafts `digests/YYYY-MM-DD.md` following `prompts/digest-style.md`
   - the **digest-editor** subagent (`.claude/agents/digest-editor.md`) verifies every summary against the fetched snippets, then the routine commits and pushes
3. A **weekly curation routine** (Mondays 11:00 UTC, prompt at `prompts/curation.md`) reviews source health and writes a report to `digests/curation/`
4. **Obsidian Git** plugin syncs the repo into your vault automatically

Items only ever appear in one digest: `data/seen_urls.json` tracks normalized URLs for 30 days, so undated scraped articles can't repeat. Freshness windows are configurable per source type and per source (`max_age_hours_by_type`, per-source `max_age_hours`) so weekly publishers aren't missed by the default 26-hour window.

## Setup

### Prerequisites

- Python 3.11+
- Obsidian with the [Obsidian Git](https://github.com/denolehov/obsidian-git) plugin
- GitHub account with push access to this repo

### Install dependencies

```bash
pip install -r requirements.txt
```

### Configure your knowledge areas

Edit `config/sources.yaml` to define your areas and sources:

```yaml
areas:
  - name: "My Area"
    emoji: "🎯"
    folder: "MyArea"          # subfolder under digests/
    tags: [digest, my-area]
    sources:
      - type: rss
        url: "https://example.com/feed.xml"
        name: "Example Feed"
      - type: youtube
        channel_id: "UCxxxxxxxxxxxxxxxxxx"
        name: "Channel Name"
      - type: podcast
        url: "https://example.com/podcast.rss"
        name: "My Podcast"
      - type: website
        url: "https://example.com"
        name: "Example Site"
      - type: rss
        url: "https://weekly.example.com/feed"
        name: "Weekly Blog"
        max_age_hours: 180    # per-source window override for infrequent publishers
```

Global per-type defaults live under `settings.max_age_hours_by_type` (currently `youtube: 80`, `podcast: 180`).

### Local testing

```bash
# Validate config without fetching
python src/fetch.py --dry-run

# Run unit tests
pip install -r requirements-dev.txt
python -m pytest -q

# Fetch with a wider time window to guarantee results (7 days)
# --no-dedup avoids touching the committed seen-URL registry
python src/fetch.py --max-age-hours 168 --no-dedup --output /tmp/test_fetch.json

# Inspect what was fetched
python -c "
import json
d = json.load(open('/tmp/test_fetch.json'))
for a in d['areas']:
    print(a['name'], ':', len(a['items']), 'items,', len(a['errors']), 'errors')
"

# Test a single area
python src/fetch.py --area "Technology" --max-age-hours 168 --no-dedup --output /tmp/tech.json
```

### CLI reference

```
python src/fetch.py [OPTIONS]

Options:
  --config PATH         Path to sources.yaml  [default: config/sources.yaml]
  --output PATH         Write JSON to file instead of stdout
  --max-age-hours INT   Force this window for ALL sources (overrides per-source/per-type config)
  --max-items INT       Max items per source  [default: 10]
  --area NAME           Fetch only this area (repeatable)
  --dry-run             Validate config and exit
  --log PATH            Write Markdown run log to file
  --seen-file PATH      Seen-URL registry for cross-run dedup  [default: data/seen_urls.json]
  --no-dedup            Skip the seen-URL registry (use for local testing)
```

## Obsidian setup

1. Install the **Obsidian Git** plugin in Obsidian
2. Point it at this repo: `https://github.com/GustavoBertaco/daily-digest`
3. Set auto-pull interval (e.g., every 30 minutes)
4. Digests appear under `digests/` in your vault, organized by area folder

## Digest format

One file per day covering all areas: `digests/YYYY-MM-DD.md`. The full
formatting and tone rules live in `prompts/digest-style.md`; in short:

```markdown
---
date: 2026-06-10
tags: [digest]
---

# Daily Digest — June 10, 2026

---

# 💻 Technology

> ⚠️ Netflix Tech Blog — no new items in window

## Uber Engineering

**[Article Title](https://link)**
2-3 sentence synthesis of why this matters and what's interesting.
```

## Mobile access

Trigger the digest manually from any device at:
[claude.ai/code/routines](https://claude.ai/code/routines)
