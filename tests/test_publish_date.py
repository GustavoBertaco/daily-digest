from datetime import datetime, timezone

from fetchers.web import _extract_publish_date


def test_article_published_time_meta():
    html = '<html><head><meta property="article:published_time" content="2026-05-15T09:00:00Z"></head></html>'
    assert _extract_publish_date(html) == datetime(2026, 5, 15, 9, 0, tzinfo=timezone.utc)


def test_jsonld_date_published():
    html = '''<html><head><script type="application/ld+json">
        {"@type": "Article", "datePublished": "2026-05-15T12:30:00-03:00"}
    </script></head></html>'''
    assert _extract_publish_date(html) == datetime(2026, 5, 15, 15, 30, tzinfo=timezone.utc)


def test_jsonld_graph_wrapper():
    html = '''<html><head><script type="application/ld+json">
        {"@graph": [{"@type": "WebSite"}, {"@type": "Article", "datePublished": "2026-05-15"}]}
    </script></head></html>'''
    assert _extract_publish_date(html) == datetime(2026, 5, 15, 0, 0, tzinfo=timezone.utc)


def test_time_element_with_pubdate():
    html = '<html><body><time pubdate datetime="2026-05-15T08:00:00Z">May 15</time></body></html>'
    assert _extract_publish_date(html) == datetime(2026, 5, 15, 8, 0, tzinfo=timezone.utc)


def test_render_timestamp_is_not_treated_as_publish_date():
    # Reproduces the Uber bug: a CDN render timestamp baked into bootstrap JS, with
    # the real publication date present only as unstructured visible text. htmldate
    # would latch onto the render time; we must return None instead.
    html = '''<html><body>
        <div class="post-meta">May 15, 2025</div>
        <h1>Building Uber's Multi-Cloud Secrets Management Platform</h1>
        <script>__uber_sites_bootstrap_loader__(fetch, true,
            {"page_generated_at":"2026-06-13T23:28:12.546Z","page_generated_uuid":"abc"});</script>
    </body></html>'''
    assert _extract_publish_date(html) is None


def test_no_signal_returns_none():
    html = '<html><head><title>No dates here</title></head><body><p>text</p></body></html>'
    assert _extract_publish_date(html) is None
