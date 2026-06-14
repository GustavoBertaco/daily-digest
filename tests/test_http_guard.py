import pytest

from fetchers import _http
from fetchers._http import _validate_url, safe_get


def test_validate_blocks_non_http_scheme():
    with pytest.raises(ValueError):
        _validate_url("file:///etc/passwd")
    with pytest.raises(ValueError):
        _validate_url("ftp://example.com/x")


def test_validate_blocks_loopback():
    with pytest.raises(ValueError):
        _validate_url("http://127.0.0.1/")


def test_validate_blocks_link_local_metadata():
    # AWS/GCP metadata endpoint — must be blocked.
    with pytest.raises(ValueError):
        _validate_url("http://169.254.169.254/latest/meta-data/")


class _Resp:
    """Minimal stand-in for requests.Response covering the redirect API safe_get uses."""

    def __init__(self, status_code, location=None):
        self.status_code = status_code
        self.headers = {"Location": location} if location else {}

    @property
    def is_redirect(self):
        return self.status_code in (301, 302, 303, 307, 308) and "Location" in self.headers

    @property
    def is_permanent_redirect(self):
        return self.status_code in (301, 308) and "Location" in self.headers


def test_safe_get_revalidates_redirect_target(monkeypatch):
    """A 302 to a private/metadata host must be blocked, not followed."""
    def fake_get(url, allow_redirects=False, **kwargs):
        return _Resp(302, location="http://169.254.169.254/latest/meta-data/")

    monkeypatch.setattr(_http._SESSION, "get", fake_get)
    with pytest.raises(ValueError):
        safe_get("https://example.com/redirector")


def test_safe_get_follows_safe_redirect(monkeypatch):
    calls = []

    def fake_get(url, allow_redirects=False, **kwargs):
        calls.append(url)
        if url == "https://example.com/start":
            return _Resp(302, location="https://example.com/final")
        return _Resp(200)

    monkeypatch.setattr(_http._SESSION, "get", fake_get)
    resp = safe_get("https://example.com/start")
    assert resp.status_code == 200
    assert calls == ["https://example.com/start", "https://example.com/final"]


def test_safe_get_caps_redirect_chain(monkeypatch):
    def fake_get(url, allow_redirects=False, **kwargs):
        return _Resp(302, location="https://example.com/loop")

    monkeypatch.setattr(_http._SESSION, "get", fake_get)
    with pytest.raises(ValueError, match="redirect"):
        safe_get("https://example.com/loop")
