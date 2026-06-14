import textwrap

import pytest

from fetch import fetch_area, load_config

_BASE_AREA = """\
settings:
  max_age_hours: 26
areas:
  - name: "Area"
    emoji: "🧪"
    folder: "Area"
    {style_line}
    sources: []
"""


def _write_config(tmp_path, style_line=""):
    path = tmp_path / "sources.yaml"
    path.write_text(textwrap.dedent(_BASE_AREA).format(style_line=style_line), encoding="utf-8")
    return str(path)


def test_summary_style_optional(tmp_path):
    cfg = load_config(_write_config(tmp_path))
    assert "summary_style" not in cfg["areas"][0]


@pytest.mark.parametrize("style", ["insight", "brief"])
def test_summary_style_valid(tmp_path, style):
    cfg = load_config(_write_config(tmp_path, f"summary_style: {style}"))
    assert cfg["areas"][0]["summary_style"] == style


def test_summary_style_invalid_exits(tmp_path):
    with pytest.raises(SystemExit):
        load_config(_write_config(tmp_path, "summary_style: verbose"))


def test_fetch_area_defaults_to_insight():
    area = {"name": "A", "emoji": "🧪", "folder": "A", "sources": []}
    assert fetch_area(area, {})["summary_style"] == "insight"


def test_fetch_area_propagates_brief():
    area = {"name": "A", "emoji": "🧪", "folder": "A", "summary_style": "brief", "sources": []}
    assert fetch_area(area, {})["summary_style"] == "brief"
