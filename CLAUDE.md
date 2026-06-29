# Project Instructions

## Untrusted sources

The `newsletter` source type (`src/fetchers/newsletter.py`) ingests forwarded
emails via a kill-the-newsletter Atom feed and is **untrusted** — anyone can email
the address. The email body is used *only* to harvest article links (filtered by a
`senders` allowlist and a scheme/denylist); its text is never summarized or placed
in the digest. Linked articles are fetched and summarized like `website` sources.
Keep this link-only model intact: never feed the email subject/body into the digest
or an LLM prompt.

Mail reaches the feed three ways: direct/auto-forward preserving the original `From:`
(verified against `senders`); a manual Gmail "Forward" (verified by the trusted
`forwarders` address *plus* the original sender quoted in the body); and a Gmail
**auto-forward**, whose sender is rewritten to a `<account>+caf_=...@gmail.com`
plus-address. An auto-forward carries no quoted original sender, so it is trusted on
the forwarder identity alone (the `+caf_` base account must be a `forwarders` entry) —
relying on the secret feed URL and the user's Gmail filter. This is a deliberate,
user-approved relaxation; the link-only model above still fully applies.

## Sync before editing studies

Files under `studies/` are sometimes edited directly on GitHub (web UI), so the local
clone can fall behind. **Before editing any file in `studies/`, sync local `main` with
the remote** (`git fetch` then `git pull --ff-only origin main`) so we don't edit a stale
copy or lose remote changes. If there are uncommitted local edits, stash them first
(`git stash` → pull → `git stash pop`). When in doubt, diff the target file against
`origin/main` before changing it.

## Git commits

Always sign commits with GPG. Use `git commit -S -m "message"` — never `git commit -m` without the `-S` flag. This applies to every commit in this repo, including during PR creation.

**Exception:** commits made by the `github-actions[bot]` in `.github/workflows/fetch.yml` (the daily content fetch) are intentionally unsigned — the runner has no signing key. This is the only sanctioned unsigned commit path.
