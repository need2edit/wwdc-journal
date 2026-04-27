#!/usr/bin/env python3
"""
Re-extract all hidden gems from each year dashboard's JS and rebuild the
embedded gem corpus in index.html (powering the shuffle button).

Run after editing year dashboards or adding a new year.

Usage:
    bin/refresh-gems.py
"""
import json
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.resolve()
LANDING = PROJECT_ROOT / "index.html"
GEMS_OUTPUT = PROJECT_ROOT / "data" / "all-gems.json"

GEM_PATTERN = re.compile(
    r'\{\s*type\s*:\s*"([^"]+)"\s*,\s*label\s*:\s*"([^"]+)"\s*,'
    r'\s*text\s*:\s*"((?:[^"\\]|\\.)*)"\s*,\s*source\s*:\s*"([^"]+)"\s*\}',
    re.DOTALL,
)


def main() -> int:
    all_gems: list[dict] = []
    for year in range(2014, 2030):
        path = PROJECT_ROOT / f"index-{year}.html"
        if not path.exists():
            continue
        html = path.read_text()
        m = re.search(r'const\s+gems\s*=\s*\[(.*?)\];', html, re.DOTALL)
        if not m:
            print(f"  {year}: no gems array found")
            continue
        matches = GEM_PATTERN.findall(m.group(1))
        print(f"  {year}: {len(matches)} gems")
        for type_, label, text, source in matches:
            text_clean = (
                text.replace('\\"', '"')
                .replace("\\'", "'")
                .replace("\\n", " ")
                .replace("\\\\", "\\")
            )
            all_gems.append({
                "year": year,
                "type": type_,
                "label": label,
                "text": text_clean,
                "source": source,
            })

    print(f"\nTotal gems: {len(all_gems)}")
    GEMS_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    GEMS_OUTPUT.write_text(json.dumps(all_gems, indent=2))
    print(f"  Wrote {GEMS_OUTPUT}")

    if not LANDING.exists():
        print(f"  ⚠ {LANDING} doesn't exist; skipping inline embed")
        return 0
    landing_html = LANDING.read_text()
    compact = json.dumps(all_gems, separators=(",", ":"), ensure_ascii=True)
    new_html = re.sub(
        r'(<script id="all-gems-data"[^>]*>)[\s\S]*?(</script>)',
        lambda m: m.group(1) + compact + m.group(2),
        landing_html,
        count=1,
    )
    if new_html == landing_html:
        print(f"  ⚠ Couldn't find <script id=\"all-gems-data\"> in {LANDING}")
        return 1
    LANDING.write_text(new_html)
    print(f"  Updated inline gems in {LANDING}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
