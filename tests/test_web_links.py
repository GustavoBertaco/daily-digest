from fetchers._http import registrable_domain
from fetchers.web import _article_links, _rss_from_link_tag


def test_registrable_domain_subdomain_collapses_to_root():
    assert registrable_domain("https://eng.uber.com/post") == "uber.com"


def test_registrable_domain_multi_label_tld_not_collapsed():
    # The bug: ".".join(netloc.split(".")[-2:]) would yield "com.br" here.
    assert registrable_domain("https://blog.example.com.br/x") == "example.com.br"
    assert registrable_domain("https://www.example.co.uk/y") == "example.co.uk"


def test_article_links_same_registrable_domain_only():
    base = "https://blog.example.com.br/"
    html = """
        <a href="https://blog.example.com.br/2026/06/some-long-article-slug">in</a>
        <a href="https://www.example.com.br/2026/06/another-long-article-slug">in2</a>
        <a href="https://unrelated.com.br/2026/06/a-different-long-article-slug">out</a>
    """
    links = _article_links(html, base)
    assert "https://blog.example.com.br/2026/06/some-long-article-slug" in links
    assert "https://www.example.com.br/2026/06/another-long-article-slug" in links
    assert all("unrelated.com.br" not in link for link in links)


def test_rss_link_tag_same_domain_only():
    base = "https://blog.example.com.br/"
    html = '''<head>
        <link rel="alternate" type="application/rss+xml" href="https://blog.example.com.br/feed">
    </head>'''
    assert _rss_from_link_tag(html, base) == "https://blog.example.com.br/feed"


def test_rss_link_tag_rejects_offsite_feed():
    base = "https://blog.example.com.br/"
    html = '''<head>
        <link rel="alternate" type="application/rss+xml" href="https://evil.com.br/feed">
    </head>'''
    assert _rss_from_link_tag(html, base) is None
