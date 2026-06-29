"""Fetch a newsletter delivered via a kill-the-newsletter Atom feed.

The email body is **untrusted** — anyone can email a kill-the-newsletter address,
so its subject/body text is never summarized or shown to an LLM. We use the email
*solely to harvest article links*, then fetch and summarize each destination page
through the same trusted path `website` sources use. Two gates keep junk and
attacker-controlled mail out:

  1. Sender allowlist — an entry is processed only if its structured
     ``<author><email>`` is in ``senders`` (a direct delivery / auto-forward that
     preserves the original From), OR it is in ``forwarders`` (a trusted address that
     manually forwarded the mail) AND the original sender quoted in the forwarded
     ``From:`` header is in ``senders``. A manual Gmail "Forward" rewrites the
     envelope sender to the forwarder, so the real sender survives only in that
     quoted header; we read it solely to verify the allowlist, never to digest it.
  2. Link-only + denylist — only ``http(s)`` ``<a href>`` URLs are taken, and
     non-article noise (unsubscribe, social shares, image CDNs, Substack app/profile
     action links) is dropped (``_extract_links`` / ``_is_article_link``).

Every fetch goes through ``safe_get`` (SSRF guard + per-hop redirect re-validation),
which also unwraps Substack tracking-redirect links to their final destination.
"""
import re
import sys
from datetime import datetime, timezone, timedelta
from urllib.parse import parse_qsl, urlparse

import feedparser
import trafilatura
from bs4 import BeautifulSoup

from . import FetchedItem
from ._http import safe_get
from .rss import _entry_published_utc
from .web import _headers

# Hosts/path fragments that are never article destinations. Matched case-insensitively
# against the URL. Keeps the curated links (real articles) and drops newsletter chrome.
_DENY_HOST_SUFFIXES = (
    "substackcdn.com",        # image/asset CDN
    "open.substack.com",      # "read in app" / restack chrome (points back at the issue)
    "kill-the-newsletter.com",  # the KTNL feed itself appears as a footer link
    "twitter.com",
    "x.com",
    "facebook.com",
    "linkedin.com",
    "instagram.com",
    "youtube.com",            # handled by the dedicated youtube source type
    "youtu.be",
)
_DENY_PATH_FRAGMENTS = (
    "/unsubscribe",
    "/manage",
    "/subscribe",
    "/account",
    "/profile",
    "/comments",
    "/comment",
    "/app/",
    "/action/",
    "/redirect/feed",
)

# Substack newsletter chrome on the bare ``substack.com`` host. The genuinely
# curated links are ``substack.com/redirect/<uuid>?j=...`` tracking URLs (unwrapped
# by safe_get to the real article); Substack's own system links instead use these
# path prefixes — profile pages, the mobile app, signup, and the base64
# ``/redirect/2/<payload>`` form (subscribe / footer / restack / disable-email).
_SUBSTACK_CHROME_PREFIXES = (
    "/@", "/app", "/signup", "/sign-in", "/note", "/notes", "/redirect/2/",
)


def _entry_sender(entry) -> str | None:
    """The sender email from the Atom ``<author><email>`` element, lowercased.

    kill-the-newsletter records the originating address in a structured author
    element, which feedparser surfaces as ``entry.author_detail.email``. Returns
    None when absent (those entries are dropped by the allowlist check).
    """
    detail = getattr(entry, "author_detail", None)
    email = (detail or {}).get("email") if isinstance(detail, dict) else getattr(detail, "email", None)
    if email and isinstance(email, str):
        return email.strip().lower()
    return None


_EMAIL_RE = r"[\w.%+\-]+@[\w.\-]+\.[A-Za-z]{2,}"

# Gmail "canonical address forward" (auto-forward) rewrites the sender to a
# plus-addressed variant of the forwarding account, e.g.
#   user+caf_=<encoded-destination>@gmail.com   (the +caf_ tag is Gmail's marker).
# Unlike a manual "Forward", an auto-forward carries no quoted original-sender
# header, so the real sender can't be re-verified from the body. We therefore
# trust it on the forwarder identity alone (base local-part on the forwarders
# allowlist) — the link-only / never-summarize-the-body model still holds.
_GMAIL_AUTOFORWARD_RE = re.compile(
    r"^(?P<base>[\w.%\-]+)\+caf_=[^@\s]*@gmail\.com$", re.IGNORECASE
)


def _gmail_autoforward_base(sender: str) -> str | None:
    """For a Gmail auto-forward sender, the underlying account address; else None.

    ``user+caf_=...@gmail.com`` -> ``user@gmail.com`` (lowercased). Returns None for
    any address that isn't a Gmail ``+caf_`` auto-forward, so ordinary plus-addressed
    mail is *not* broadened into the forwarder allowlist.
    """
    m = _GMAIL_AUTOFORWARD_RE.match(sender)
    return f"{m.group('base').lower()}@gmail.com" if m else None


def _forwarded_original_sender(html: str) -> str | None:
    """Original sender from a forwarded email's quoted ``From:`` header, lowercased.

    A manual Gmail "Forward" rewrites the envelope sender to the forwarder, leaving
    the real sender only in the ``---------- Forwarded message ----------`` /
    ``From:`` block. We read that block purely to extract an address for the
    allowlist check — never to digest content, and only ever for mail that already
    cleared the trusted-``forwarders`` gate, so a spoofed body can't bypass it.
    """
    text = BeautifulSoup(html, "html.parser").get_text("\n")
    marker = re.search(r"forwarded message", text, re.IGNORECASE)
    segment = text[marker.start():] if marker else text
    m = re.search(r"From:\s*[^\n]*?<?(" + _EMAIL_RE + r")>?", segment, re.IGNORECASE)
    return m.group(1).strip().lower() if m else None


def _entry_is_allowed(entry, senders: set[str], forwarders: set[str], body: str) -> bool:
    """True if the entry came from an allowed sender, directly or via a trusted forward."""
    sender = _entry_sender(entry)
    if sender is None:
        return False
    if sender in senders:
        return True
    if sender in forwarders:
        original = _forwarded_original_sender(body)
        return original is not None and original in senders
    # Gmail auto-forward: sender is a +caf_ plus-address of a trusted forwarder.
    # No quoted original sender exists to verify, so trust rests on the forwarder
    # identity plus the secret kill-the-newsletter feed URL (accepted tradeoff).
    base = _gmail_autoforward_base(sender)
    if base is not None and base in forwarders:
        return True
    return False


def _is_article_link(url: str) -> bool:
    """True only for http(s) links that look like real article destinations.

    Applied twice: to the raw ``<a href>`` at harvest time, and again to the final
    URL after ``safe_get`` unwraps any tracking redirect — so a redirect that
    resolves to newsletter chrome (app, image viewer, the issue's own page) is
    dropped even though its wrapper looked benign.
    """
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        return False
    host = (parsed.hostname or "").lower()
    if not host:
        return False
    if any(host == d or host.endswith("." + d) for d in _DENY_HOST_SUFFIXES):
        return False
    path = parsed.path.lower()
    if any(frag in path for frag in _DENY_PATH_FRAGMENTS):
        return False
    if host == "substack.com" and path.startswith(_SUBSTACK_CHROME_PREFIXES):
        return False
    # Substack "view image in post" links resolve to the issue page with an ?img=
    # query — an image viewer, never an article.
    if "img" in {k for k, _ in parse_qsl(parsed.query)}:
        return False
    return True


def _extract_links(html: str) -> list[str]:
    """Harvest article URLs from email HTML — links only, never the surrounding text.

    Only ``<a href>`` values survive; the email's prose is deliberately ignored so no
    attacker-controlled text reaches the digest. Applies the scheme + denylist filter
    and dedups while preserving first-seen order.
    """
    soup = BeautifulSoup(html, "html.parser")
    seen: set[str] = set()
    links: list[str] = []
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if not href or not _is_article_link(href):
            continue
        if href in seen:
            continue
        seen.add(href)
        links.append(href)
    return links


def fetch_newsletter(
    url: str,
    source_name: str,
    senders: list[str],
    forwarders: list[str] | None = None,
    max_age_hours: int = 180,
    max_items: int = 10,
    timeout: int = 10,
    user_agent: str = "daily-digest/1.0",
) -> list[FetchedItem]:
    allow = {s.strip().lower() for s in senders if isinstance(s, str)}
    allow_fwd = {s.strip().lower() for s in (forwarders or []) if isinstance(s, str)}
    try:
        r = safe_get(url, headers={"User-Agent": user_agent}, timeout=timeout)
        r.raise_for_status()
        feed = feedparser.parse(r.content)
    except Exception as exc:
        print(f"ERROR fetch_newsletter({url}): {exc}", file=sys.stderr)
        return []

    if not feed.entries:
        return []

    cutoff = datetime.now(tz=timezone.utc) - timedelta(hours=max_age_hours)

    # Collect candidate links from every in-window entry sent by an allowed sender.
    # The newsletter *issue* is the fresh unit: each link inherits its issue's date,
    # so a weekly roundup can legitimately surface older-than-26h articles.
    candidates: list[tuple[str, datetime | None]] = []
    seen_links: set[str] = set()
    for entry in feed.entries:
        pub = _entry_published_utc(entry)
        if pub is not None and pub < cutoff:
            continue
        body = ""
        content = getattr(entry, "content", None)
        if content and isinstance(content, list):
            body = content[0].get("value", "") or ""
        if not body:
            body = getattr(entry, "summary", "") or ""
        if not _entry_is_allowed(entry, allow, allow_fwd, body):
            continue
        for link in _extract_links(body):
            if link in seen_links:
                continue
            seen_links.add(link)
            candidates.append((link, pub))

    items: list[FetchedItem] = []
    for link, pub in candidates:
        if len(items) >= max_items:
            break
        try:
            ar = safe_get(link, headers=_headers(url), timeout=timeout)
            ar.raise_for_status()
            final_url = ar.url or link  # safe_get unwraps tracking redirects
            # A wrapper that looked like a real link may resolve to chrome (the app,
            # an image viewer, the issue's own page). Re-check the unwrapped URL.
            if not _is_article_link(final_url):
                continue
            metadata = trafilatura.extract_metadata(ar.text)
            body = trafilatura.extract(ar.text) or ""
            if not body:
                continue
            title = (metadata.title if metadata else "") or final_url
            items.append(FetchedItem(
                title=title,
                url=final_url,
                published=pub.isoformat() if pub else "",
                content_snippet=body[:500],
                source_name=source_name,
                source_type="website",  # flows through the insight pipeline
                area_name="",
            ))
        except Exception:
            continue

    return items
