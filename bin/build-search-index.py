#!/usr/bin/env python3
"""
Build a cross-year search index from all 12 year dashboards and embed it
into the landing page.

Indexes:
- Sessions (from sessionTitles map in each dashboard)
- Pathways (from pathways array)
- Clusters (from clusters array)
- Gems (from gems array — with docUrl if present)
- Topics (from topicData array)

Output:
- data/search-index.json (canonical, pretty-printed for inspection)
- inline embedded in index.html as <script id="search-index">

Usage:
    bin/build-search-index.py
"""
import json
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.resolve()
LANDING = PROJECT_ROOT / "index.html"
INDEX_OUTPUT = PROJECT_ROOT / "data" / "search-index.json"


def find_array_body(html: str, var_name: str) -> "str | None":
    """Extract the body of `const var_name = [ ... ];`"""
    m = re.search(rf"const\s+{var_name}\s*=\s*(\[.*?\]);", html, re.DOTALL)
    return m.group(1) if m else None


def find_object_body(html: str, var_name: str) -> "str | None":
    """Extract the body of `const var_name = { ... };`"""
    m = re.search(rf"const\s+{var_name}\s*=\s*(\{{.*?\}});", html, re.DOTALL)
    return m.group(1) if m else None


SESSION_TITLE_RE = re.compile(r'"(\d+)"\s*:\s*"((?:[^"\\]|\\.)*)"')
PATHWAY_RE = re.compile(r"\{[^{}]*?id\s*:\s*\"([^\"]+)\"[^{}]*?name\s*:\s*\"([^\"]+)\"[^{}]*?\}", re.DOTALL)
PATHWAY_DESC_RE = re.compile(r"desc(?:ription)?\s*:\s*\"((?:[^\"\\]|\\.)*)\"")
CLUSTER_RE = re.compile(
    r"\{\s*name\s*:\s*\"([^\"]+)\"\s*,\s*desc(?:ription)?\s*:\s*\"((?:[^\"\\]|\\.)*)\"\s*,\s*sessions\s*:\s*\[([^\]]*)\]",
    re.DOTALL,
)
GEM_RE = re.compile(
    r'\{\s*type\s*:\s*"([^"]+)"\s*,\s*label\s*:\s*"([^"]+)"\s*,'
    r'\s*text\s*:\s*"((?:[^"\\]|\\.)*)"\s*,\s*source\s*:\s*"([^"]+)"'
    r'(?:\s*,\s*docUrl\s*:\s*"([^"]+)")?\s*\}',
    re.DOTALL,
)
TOPIC_RE = re.compile(r"\{\s*name\s*:\s*\"([^\"]+)\"\s*,\s*count\s*:\s*(\d+)")


def unescape(s: str) -> str:
    return (s.replace('\\"', '"').replace("\\'", "'")
            .replace("\\n", " ").replace("\\\\", "\\"))


def extract_year(year: int) -> list[dict]:
    path = PROJECT_ROOT / f"index-{year}.html"
    if not path.exists():
        return []
    html = path.read_text()
    items: list[dict] = []

    # 1. Sessions
    titles_body = find_object_body(html, "sessionTitles")
    if titles_body:
        for sid, title in SESSION_TITLE_RE.findall(titles_body):
            items.append({
                "y": year, "k": "S",
                "i": sid, "t": unescape(title),
            })

    # 2. Pathways
    pathways_body = find_array_body(html, "pathways")
    if pathways_body:
        for m in PATHWAY_RE.finditer(pathways_body):
            pid, name = m.group(1), m.group(2)
            obj_text = m.group(0)
            desc_m = PATHWAY_DESC_RE.search(obj_text)
            desc = unescape(desc_m.group(1)) if desc_m else ""
            items.append({
                "y": year, "k": "P",
                "i": pid, "t": unescape(name), "d": desc,
            })

    # 3. Clusters
    clusters_body = find_array_body(html, "clusters")
    if clusters_body:
        for m in CLUSTER_RE.finditer(clusters_body):
            name, desc, _ = m.group(1), m.group(2), m.group(3)
            items.append({
                "y": year, "k": "C",
                "i": name, "t": unescape(name), "d": unescape(desc),
            })

    # 4. Gems
    gems_body = find_array_body(html, "gems")
    if gems_body:
        for type_, label, text, source, doc_url in GEM_RE.findall(gems_body):
            entry = {
                "y": year, "k": "G",
                "i": source, "t": unescape(text), "l": label,
            }
            if doc_url:
                entry["du"] = doc_url
            items.append(entry)

    # 5. Topics
    topics_body = find_array_body(html, "topicData")
    if topics_body:
        for m in TOPIC_RE.finditer(topics_body):
            name, count = m.group(1), int(m.group(2))
            items.append({
                "y": year, "k": "T",
                "i": name, "t": name, "c": count,
            })

    return items


def main() -> int:
    print("Building cross-year search index...")
    all_items: list[dict] = []
    for year in range(2014, 2026):
        items = extract_year(year)
        kinds: dict[str, int] = {}
        for it in items:
            kinds[it["k"]] = kinds.get(it["k"], 0) + 1
        kind_summary = ", ".join(
            f"{n}{k}" for k, n in sorted(kinds.items())
        )
        print(f"  {year}: {len(items):4d} items ({kind_summary})")
        all_items.extend(items)

    print(f"\nTotal: {len(all_items)} items")

    # Save canonical
    INDEX_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    INDEX_OUTPUT.write_text(json.dumps(all_items, indent=2))
    print(f"  Wrote {INDEX_OUTPUT} ({INDEX_OUTPUT.stat().st_size // 1024} KB)")

    # Embed compact JSON in landing page
    if not LANDING.exists():
        print(f"  ⚠ {LANDING} doesn't exist; skipping embed")
        return 0
    landing_html = LANDING.read_text()
    compact = json.dumps(all_items, separators=(",", ":"), ensure_ascii=True)
    if '<script id="search-index"' in landing_html:
        new_html = re.sub(
            r'(<script id="search-index"[^>]*>)[\s\S]*?(</script>)',
            lambda m: m.group(1) + compact + m.group(2),
            landing_html,
            count=1,
        )
        LANDING.write_text(new_html)
        print(f"  Updated inline search index in {LANDING} ({len(compact) // 1024} KB compact)")
    else:
        print(f"  ⚠ <script id=\"search-index\"> not found in {LANDING} — add it before re-running")
        print(f"     Hint: place near the existing <script id=\"all-gems-data\"> tag")
    return 0


if __name__ == "__main__":
    sys.exit(main())
