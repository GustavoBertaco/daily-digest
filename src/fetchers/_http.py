import ipaddress
import socket
from urllib.parse import urljoin, urlparse

import requests
import tldextract
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

_DEFAULT_TIMEOUT = 10
_MAX_REDIRECTS = 5

# Resolve registrable domains offline: don't fetch the public suffix list at
# runtime (keeps CI deterministic and avoids a network call on import).
_extract = tldextract.TLDExtract(suffix_list_urls=())


def registrable_domain(url: str) -> str:
    """eTLD+1 for same-site checks, e.g. blog.example.com.br -> example.com.br.

    Naively taking the last two netloc labels collapses every *.com.br (or *.co.uk)
    onto the public suffix itself, defeating same-domain restrictions.
    """
    return _extract(url).registered_domain


def _is_private_ip(hostname: str) -> bool:
    try:
        for _, _, _, _, sockaddr in socket.getaddrinfo(hostname, None):
            ip = ipaddress.ip_address(sockaddr[0])
            if (ip.is_private or ip.is_loopback or ip.is_link_local
                    or ip.is_reserved or ip.is_multicast):
                return True
    except Exception:
        pass
    return False


def _validate_url(url: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise ValueError(f"Blocked non-http(s) URL scheme: {parsed.scheme!r}")
    if _is_private_ip(parsed.hostname or ""):
        raise ValueError(f"Blocked request to private/reserved host: {parsed.hostname!r}")


def _build_session() -> requests.Session:
    session = requests.Session()
    retry = Retry(
        total=2,
        backoff_factor=0.5,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=("GET",),
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


_SESSION = _build_session()


def safe_get(url: str, **kwargs) -> requests.Response:
    """GET with SSRF guards and transient-failure retries.

    Validates scheme + resolved IP on the initial URL *and on every redirect hop*:
    a single up-front check is bypassable by a 3xx to a private/metadata host, since
    requests re-resolves DNS when following redirects. We follow redirects manually
    so each Location is re-validated. A default timeout is enforced so no caller can
    hang the run.
    """
    kwargs.setdefault("timeout", _DEFAULT_TIMEOUT)
    kwargs.pop("allow_redirects", None)  # handled manually to re-validate each hop

    current = url
    for _ in range(_MAX_REDIRECTS + 1):
        _validate_url(current)
        resp = _SESSION.get(current, allow_redirects=False, **kwargs)
        if resp.is_redirect or resp.is_permanent_redirect:
            location = resp.headers.get("Location")
            if not location:
                return resp
            current = urljoin(current, location)
            continue
        return resp
    raise ValueError(f"Too many redirects (>{_MAX_REDIRECTS}) for {url!r}")
