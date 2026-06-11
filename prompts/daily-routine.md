# Daily Digest Routine — canonical prompt

Canonical prompt text for the daily cloud routine (`trig_01GujRjAfZenCceEfNbvcboe`,
10:00 UTC daily). When this file changes, update the routine via the `/schedule`
skill so the deployed prompt matches.

---

Generate today's daily digest. You are a thin orchestrator — the digest
intelligence lives in this repo's agent and prompt files.

1. `git pull --rebase` to get the latest fetched data.

2. Check data freshness: `python src/check_freshness.py --max-age-hours 3`
   - **FRESH** (exit 0): continue to step 4.
   - **STALE or MISSING** (exit 1): continue to step 3.

3. Fallback fetch: run
   `pip install -r requirements.txt -q && python src/fetch.py --output data/latest_fetch.json --log logs/latest_run.md`
   - If it succeeds: commit the refreshed data with
     `git commit -S -m "chore: fallback fetch YYYY-MM-DD"` and continue with fresh data.
   - If it also fails: continue with the stale `data/latest_fetch.json`, and pass
     a staleness flag (with the `fetched_at` value and its age in hours) to the
     writer so the digest carries the staleness banner.

4. Invoke the **digest-writer** subagent to draft `digests/YYYY-MM-DD.md` from
   `data/latest_fetch.json`, passing the staleness flag if applicable.

5. Invoke the **digest-editor** subagent on the draft. It edits in place and
   reports PASS or a list of corrections.

6. Commit and push:
   `git add digests/ && git commit -S -m "digest: YYYY-MM-DD" && git push`
   If the push is rejected, `git pull --rebase` and push again.

**Fallback if subagents are unavailable:** if the digest-writer/digest-editor
subagents from `.claude/agents/` cannot be invoked in this environment, do the
same work inline: read `prompts/digest-style.md`, draft the digest following it
exactly, then re-read `data/latest_fetch.json` and self-review the draft using
the checklist in `.claude/agents/digest-editor.md` before committing.

All commits must be GPG-signed (`git commit -S`).
