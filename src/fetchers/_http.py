import ipaddress
import socket
from urllib.parse import urlparse

import requests


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


def safe_get(url: str, **kwargs) -> requests.Response:
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise ValueError(f"Blocked non-http(s) URL scheme: {parsed.scheme!r}")
    if _is_private_ip(parsed.hostname or ""):
        raise ValueError(f"Blocked request to private/reserved host: {parsed.hostname!r}")
    return requests.get(url, **kwargs)
