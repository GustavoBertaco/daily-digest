# daily-digest

Automated daily digest aggregator. A scheduled remote Claude agent fetches content from RSS feeds, YouTube channels, podcasts, and websites — then writes concise Obsidian-compatible `.md` summaries organized by knowledge area.

## How it works

1. A Claude CCR routine runs daily at **7:00 AM São Paulo (10:00 UTC)**
2. It runs `src/fetch.py` to collect raw content from all configured sources
3. Claude synthesizes the content into digest `.md` files under `digests/`
4. The files are committed and pushed to this repo
5. **Obsidian Git** plugin syncs the repo into your vault automatically

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
```

### Local testing

```bash
# Validate config without fetching
python src/fetch.py --dry-run

# Fetch with a wider time window to guarantee results (7 days)
python src/fetch.py --max-age-hours 168 --output /tmp/test_fetch.json

# Inspect what was fetched
python -c "
import json
d = json.load(open('/tmp/test_fetch.json'))
for a in d['areas']:
    print(a['name'], ':', len(a['items']), 'items,', len(a['errors']), 'errors')
"

# Test a single area
python src/fetch.py --area "Technology" --max-age-hours 168 --output /tmp/tech.json
```

### CLI reference

```
python src/fetch.py [OPTIONS]

Options:
  --config PATH         Path to sources.yaml  [default: config/sources.yaml]
  --output PATH         Write JSON to file instead of stdout
  --max-age-hours INT   Hours lookback window  [default: 24]
  --max-items INT       Max items per source  [default: 10]
  --area NAME           Fetch only this area (repeatable)
  --dry-run             Validate config and exit
```

## Obsidian setup

1. Install the **Obsidian Git** plugin in Obsidian
2. Point it at this repo: `https://github.com/GustavoBertaco/daily-digest`
3. Set auto-pull interval (e.g., every 30 minutes)
4. Digests appear under `digests/` in your vault, organized by area folder

## Digest format

Each area produces one file per day: `digests/{folder}/YYYY-MM-DD.md`

```markdown
---
date: 2026-06-04
area: Technology
tags: [digest, technology]
---

# 💻 Technology Digest — June 4, 2026

> 8 items from 4 sources. Fetched at 10:02 UTC.

## 📰 Hacker News

### [Article Title](https://link)
*Published: June 4, 2026*

2-3 sentence synthesis of why this matters and what's interesting.
```

## Mobile access

Trigger the digest manually from any device at:
[claude.ai/code/routines](https://claude.ai/code/routines)
