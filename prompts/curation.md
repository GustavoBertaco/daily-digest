# Weekly Source Curation Routine — canonical prompt

Canonical prompt text for the weekly curation cloud routine (Mondays 11:00 UTC,
after the daily digest run). When this file changes, update the routine via the
`/schedule` skill.

---

Review the health of the digest's content sources and report. You propose —
you never add or remove sources yourself.

1. `git pull --rebase`.

2. Gather evidence for the last 7 days:
   - `git log -7 -p -- logs/latest_run.md` for the per-source status tables
     (items per run, errors, "no items in window" streaks).
   - If run logs are missing, fall back to the history of `data/latest_fetch.json`.
   - Read `config/sources.yaml` for the current source list and any existing
     `# CURATION(...)` comments.

3. Build a per-source 7-day hit table: items/day, error count, empty-day streak.

4. Flag:
   - **Dormant**: 0 items in 14+ days (count previous `# CURATION` observations
     to extend the window beyond 7 days).
   - **Failing**: recurring errors across multiple runs.
   - **Noisy**: consistently >7 items/day — propose a per-source `max_items`
     cap or removal.

5. Product Management gap: the area has no sources. Use web search to propose
   3-5 candidates, RSS-first (e.g. Lenny's Newsletter, Mind the Product, SVPG
   blog). Verify each proposed feed URL actually serves RSS/Atom before
   recommending it. Propose only — do not edit the sources list.

6. Output, committed with `git commit -S`:
   - Update `config/sources.yaml` ONLY by adding/refreshing
     `# CURATION(YYYY-MM-DD): <observation>` comments next to flagged sources.
     Never add, remove, or modify the sources themselves.
   - Write `digests/curation/YYYY-Www.md` (ISO week, e.g. `2026-W25.md`) with
     the hit-rate table, flags, and recommendations — it syncs to Obsidian so
     the user reads it there. Frontmatter: `date`, `tags: [digest, curation]`.

7. Push (`git pull --rebase` first if rejected).
