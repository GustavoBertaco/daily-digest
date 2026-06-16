"""
Entry point: reads config/sources.yaml, fetches all sources, writes JSON.

Usage:
  python src/fetch.py [--config PATH] [--output PATH] [--log PATH]
                      [--max-age-hours N] [--max-items N] [--area NAME] [--dry-run]
"""
import argparse
import json
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

import yaml

from fetchers import FetchedItem
from fetchers.rss import fetch_rss
from fetchers.youtube import fetch_youtube
from fetchers.web import fetch_website
from seen import load_seen, normalize_url

_REQUIRED_AREA_KEYS = {"name", "emoji", "folder", "sources"}
_VALID_SUMMARY_STYLES = {"insight", "brief"}
_DEFAULT_SUMMARY_STYLE = "insight"
_REQUIRED_SOURCE_KEYS_BY_TYPE = {
    "rss": {"url"},
    "podcast": {"url"},
    "youtube": {"channel_id"},
    "website": {"url"},
}


def load_config(config_path: str) -> dict:
    path = Path(config_path)
    if not path.exists():
        print(f"ERROR: config file not found: {config_path}", file=sys.stderr)
        sys.exit(1)
    try:
        with open(path, encoding="utf-8") as f:
            cfg = yaml.safe_load(f)
    except yaml.YAMLError as e:
        print(f"ERROR: invalid YAML in {config_path}: {e}", file=sys.stderr)
        sys.exit(1)

    areas = cfg.get("areas")
    if not areas or not isinstance(areas, list):
        print("ERROR: sources.yaml must have a non-empty 'areas' list", file=sys.stderr)
        sys.exit(1)

    for area in areas:
        missing = _REQUIRED_AREA_KEYS - area.keys()
        if missing:
            print(f"ERROR: area '{area.get('name', '?')}' missing fields: {missing}", file=sys.stderr)
            sys.exit(1)
        if "summary_style" in area and area["summary_style"] not in _VALID_SUMMARY_STYLES:
            print(
                f"ERROR: area '{area['name']}' summary_style must be one of "
                f"{sorted(_VALID_SUMMARY_STYLES)}",
                file=sys.stderr,
            )
            sys.exit(1)
        for src in area["sources"]:
            src_type = src.get("type")
            required = _REQUIRED_SOURCE_KEYS_BY_TYPE.get(src_type)
            if required is None:
                print(f"ERROR: unknown source type '{src_type}' in area '{area['name']}'", file=sys.stderr)
                sys.exit(1)
            missing_src = required - src.keys()
            if missing_src:
                print(f"ERROR: source '{src.get('name','?')}' missing fields: {missing_src}", file=sys.stderr)
                sys.exit(1)
            if "max_age_hours" in src and (
                not isinstance(src["max_age_hours"], int) or src["max_age_hours"] <= 0
            ):
                print(f"ERROR: source '{src.get('name','?')}' max_age_hours must be a positive int", file=sys.stderr)
                sys.exit(1)

    settings = cfg.get("settings") or {}
    by_type = settings.get("max_age_hours_by_type") or {}
    for src_type, hours in by_type.items():
        if src_type not in _REQUIRED_SOURCE_KEYS_BY_TYPE:
            print(f"ERROR: max_age_hours_by_type has unknown source type '{src_type}'", file=sys.stderr)
            sys.exit(1)
        if not isinstance(hours, int) or hours <= 0:
            print(f"ERROR: max_age_hours_by_type['{src_type}'] must be a positive int", file=sys.stderr)
            sys.exit(1)

    if "request_timeout_seconds" in settings and (
        not isinstance(settings["request_timeout_seconds"], int)
        or settings["request_timeout_seconds"] <= 0
    ):
        print("ERROR: settings.request_timeout_seconds must be a positive int", file=sys.stderr)
        sys.exit(1)
    if "user_agent" in settings and not (
        isinstance(settings["user_agent"], str) and settings["user_agent"].strip()
    ):
        print("ERROR: settings.user_agent must be a non-empty string", file=sys.stderr)
        sys.exit(1)

    return cfg


def resolve_max_age(src: dict, settings: dict) -> int:
    """Freshness window for one source: CLI override > source > type default > global."""
    if settings.get("_max_age_forced"):
        return settings["max_age_hours"]
    if "max_age_hours" in src:
        return src["max_age_hours"]
    by_type = settings.get("max_age_hours_by_type") or {}
    if src.get("type") in by_type:
        return by_type[src["type"]]
    return settings.get("max_age_hours", 24)


def _fetch_one_source(
    src: dict, area_name: str, max_age: int, max_items: int,
    timeout: int, user_agent: str,
) -> tuple[list[FetchedItem], list[dict]]:
    src_type = src["type"]
    src_name = src.get("name", src_type)
    items: list[FetchedItem] = []
    errors: list[dict] = []
    try:
        if src_type in ("rss", "podcast"):
            items = fetch_rss(src["url"], src_name, source_type=src_type,
                              max_age_hours=max_age, max_items=max_items,
                              timeout=timeout, user_agent=user_agent)
        elif src_type == "youtube":
            items = fetch_youtube(src["channel_id"], src_name,
                                  max_age_hours=max_age, max_items=max_items,
                                  timeout=timeout, user_agent=user_agent)
        elif src_type == "website":
            # website keeps its browser User-Agent (config user_agent would trip WAFs)
            items = fetch_website(src["url"], src_name,
                                  max_age_hours=max_age, max_items=max_items,
                                  timeout=timeout)
        for item in items:
            item["area_name"] = area_name
        if not items:
            errors.append({
                "source_name": src_name,
                "error": "No items returned (feed empty or all outside time window)",
            })
    except Exception as e:
        errors.append({"source_name": src_name, "error": str(e)})
    return items, errors


def fetch_area(area: dict, settings: dict) -> dict:
    max_items = settings.get("max_items_per_source", 10)
    timeout = settings.get("request_timeout_seconds", 10)
    user_agent = settings.get("user_agent", "daily-digest/1.0")

    result = {
        "name": area["name"],
        "emoji": area["emoji"],
        "folder": area["folder"],
        "summary_style": area.get("summary_style", _DEFAULT_SUMMARY_STYLE),
        "tags": area.get("tags", []),
        "items": [],
        "errors": [],
    }

    if not area["sources"]:
        return result

    max_workers = min(len(area["sources"]), 8)
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = [
            pool.submit(_fetch_one_source, src, area["name"],
                        resolve_max_age(src, settings), max_items, timeout, user_agent)
            for src in area["sources"]
        ]
        for future in futures:  # preserve source order
            items, errors = future.result()
            result["items"].extend(items)
            result["errors"].extend(errors)

    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch daily digest content")
    parser.add_argument("--config", default="config/sources.yaml")
    parser.add_argument("--output", default=None, help="Write JSON to file (default: stdout)")
    parser.add_argument("--max-age-hours", type=int, default=None,
                        help="Force this window for ALL sources, overriding per-source/per-type config")
    parser.add_argument("--max-items", type=int, default=None)
    parser.add_argument("--area", action="append", default=[], dest="areas",
                        help="Fetch only this area name (repeatable)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Validate config and print summary without fetching")
    parser.add_argument("--log", default=None, help="Write Markdown run log to file")
    parser.add_argument("--seen-file", default="data/seen_urls.json",
                        help="Seen-URL registry path for dedup across runs")
    parser.add_argument("--no-dedup", action="store_true",
                        help="Skip the seen-URL registry (no filtering, no registry update)")
    args = parser.parse_args()

    cfg = load_config(args.config)
    settings = cfg.get("settings", {})
    if args.max_age_hours is not None:
        settings["max_age_hours"] = args.max_age_hours
        settings["_max_age_forced"] = True
    if args.max_items is not None:
        settings["max_items_per_source"] = args.max_items

    if args.dry_run:
        print(f"Config OK — {len(cfg['areas'])} areas:")
        for a in cfg["areas"]:
            print(f"  {a['emoji']} {a['name']} ({len(a['sources'])} sources)")
        sys.exit(0)

    fetched_at = datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    output = {
        "fetched_at": fetched_at,
        "max_age_hours": settings.get("max_age_hours", 24),
        "areas": [],
    }

    all_empty = True
    areas = [a for a in cfg["areas"] if not args.areas or a["name"] in args.areas]
    for area in areas:
        output["areas"].append(fetch_area(area, settings))

    if not args.no_dedup:
        # Filter out URLs already committed to the registry by a prior digest.
        # The registry is written at *digest* time (src/mark_seen.py), not here,
        # so an item that is fetched but never makes it into a digest can still
        # resurface on a later run instead of being silently lost.
        seen_path = Path(args.seen_file)
        seen = load_seen(seen_path)
        deduped_count = 0
        for area_result in output["areas"]:
            kept: list[FetchedItem] = []
            deduped_by_source: dict[str, int] = {}
            for item in area_result["items"]:
                if normalize_url(item["url"]) in seen:
                    deduped_count += 1
                    name = item.get("source_name", "")
                    deduped_by_source[name] = deduped_by_source.get(name, 0) + 1
                    continue
                kept.append(item)
            area_result["items"] = kept
            # Surface sources whose every item was already digested, so they don't
            # vanish from the run log (they fetched fine — the content is just
            # stale). A source with surviving items is reported via those instead.
            kept_sources = {i.get("source_name", "") for i in kept}
            area_result["deduped_sources"] = {
                name: n for name, n in deduped_by_source.items()
                if name and name not in kept_sources
            }
        output["deduped_count"] = deduped_count
        if deduped_count:
            print(f"Skipped {deduped_count} previously-digested items", file=sys.stderr)

    for area_result in output["areas"]:
        if area_result["items"]:
            all_empty = False

    json_out = json.dumps(output, ensure_ascii=False, indent=2)

    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(json_out, encoding="utf-8")
        print(f"Wrote {len(json_out)} bytes to {args.output}", file=sys.stderr)
    else:
        print(json_out)

    if all_empty:
        print("WARNING: all areas returned 0 items", file=sys.stderr)

    if args.log:
        _write_log(args.log, output)


def _write_log(log_path: str, output: dict) -> None:
    from datetime import datetime as dt
    fetched_at = output["fetched_at"]
    date_str = fetched_at[:10]
    try:
        date_label = dt.strptime(date_str, "%Y-%m-%d").strftime("%B %-d, %Y")
    except ValueError:
        date_label = date_str

    rows: list[str] = []
    total_items = 0
    total_errors = 0
    empty_areas: list[str] = []

    for area in output["areas"]:
        area_name = area["name"]
        area_items = len(area["items"])
        total_items += area_items

        # Group errors by source_name for clean display
        error_map: dict[str, str] = {}
        for e in area.get("errors", []):
            error_map[e["source_name"]] = e["error"]

        # Collect source names from items + errors
        source_names: list[str] = []
        seen: set[str] = set()
        for item in area["items"]:
            sn = item.get("source_name", "")
            if sn and sn not in seen:
                seen.add(sn)
                source_names.append(sn)
        for e in area.get("errors", []):
            sn = e["source_name"]
            if sn not in seen:
                seen.add(sn)
                source_names.append(sn)
        deduped_sources = area.get("deduped_sources", {})
        for sn in deduped_sources:
            if sn not in seen:
                seen.add(sn)
                source_names.append(sn)

        if area_items == 0:
            empty_areas.append(area_name)

        for sn in source_names:
            src_items = sum(1 for i in area["items"] if i.get("source_name") == sn)
            if sn in error_map:
                status = f"❌ {error_map[sn]}"
                total_errors += 1
            elif sn in deduped_sources:
                n = deduped_sources[sn]
                status = f"↩️ {n} already digested"
            elif src_items == 0:
                status = "⚠️ no items in window"
            else:
                status = "✅"
            rows.append(f"| {sn} | {area_name} | {src_items} | {status} |")

    table = "\n".join(rows) if rows else "| — | — | — | no sources configured |"

    empty_note = (
        f"\n- Areas with 0 items: {len(empty_areas)} ({', '.join(empty_areas)})"
        if empty_areas else ""
    )

    log_md = (
        f"---\ndate: {date_str}\ntype: run-log\n---\n\n"
        f"# Digest Run Log — {date_label}\n"
        f"Fetched at: {fetched_at} | default window: {output['max_age_hours']}h "
        f"(per-source/per-type overrides may differ)\n\n"
        f"## Results by source\n\n"
        f"| Source | Area | Items | Status |\n"
        f"|--------|------|-------|--------|\n"
        f"{table}\n\n"
        f"## Summary\n\n"
        f"- Total items fetched: {total_items}\n"
        f"- Sources with errors: {total_errors}"
        f"{empty_note}\n"
    )

    Path(log_path).parent.mkdir(parents=True, exist_ok=True)
    Path(log_path).write_text(log_md, encoding="utf-8")
    print(f"Wrote run log to {log_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
