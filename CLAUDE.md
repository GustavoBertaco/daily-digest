# Project Instructions

## Git commits

Always sign commits with GPG. Use `git commit -S -m "message"` — never `git commit -m` without the `-S` flag. This applies to every commit in this repo, including during PR creation.

**Exception:** commits made by the `github-actions[bot]` in `.github/workflows/fetch.yml` (the daily content fetch) are intentionally unsigned — the runner has no signing key. This is the only sanctioned unsigned commit path.
