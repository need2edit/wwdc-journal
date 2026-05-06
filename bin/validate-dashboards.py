#!/usr/bin/env python3
"""
Validate every year dashboard, the modernization guide, the featured guide,
the marketing guide, and the landing page.

Checks:
- HTML file exists and is non-empty
- Single <script> block parses as JavaScript (uses node)
- Required CSS classes / JS primitives are present
- Required data structures are populated (sessionTitles, pathways, etc.)

Usage:
    bin/validate-dashboards.py
    bin/validate-dashboards.py --strict   # exit 1 on any warning
"""
import argparse
import re
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.resolve()


YEAR_DASHBOARD_REQUIREMENTS = [
    ("WWDC_YEAR constant",      lambda y: f"WWDC_YEAR = {y}"),
    ("function wrapTitle",      lambda y: "function wrapTitle"),
    ("function escXml",         lambda y: "function escXml"),
    ("badges-row container",    lambda y: ".badges-row"),
    ("breadcrumb back link",    lambda y: 'class="breadcrumb"'),
    ("search input",            lambda y: 'id="search-input"'),
    ("setupSearch function",    lambda y: "function setupSearch"),
    ("sessionTitles map",       lambda y: "const sessionTitles"),
    ("pathways array",          lambda y: "const pathways"),
    ("clusters array",          lambda y: "const clusters"),
    ("gems array",              lambda y: "const gems"),
    ("deltas array",            lambda y: "const deltas"),
]

GUIDE_REQUIREMENTS = {
    "modernization.html": [
        ("year picker",       "year-buttons"),
        ("phase blocks",      "phase-block"),
        ("checkable items",   "function toggleItem"),
        ("localStorage key",  "wwdc_modernization_progress"),
    ],
    "featured.html": [
        ("phase blocks",      "phase-block"),
        ("checkable items",   "function toggleItem"),
        ("localStorage key",  "wwdc_featured_progress"),
        ("quick wins tab",    "renderQuickWins"),
    ],
    "marketing.html": [
        ("phase blocks",      "phase-block"),
        ("checkable items",   "function toggleItem"),
        ("localStorage key",  "wwdc_marketing_progress"),
        ("owner role tags",   "role-marketing"),
    ],
    "accessibility.html": [
        ("phase blocks",      "phase-block"),
        ("checkable items",   "function toggleItem"),
        ("localStorage key",  "wwdc_accessibility_progress"),
        ("quick wins tab",    "renderQuickWins"),
    ],
    "performance.html": [
        ("phase blocks",      "phase-block"),
        ("checkable items",   "function toggleItem"),
        ("localStorage key",  "wwdc_performance_progress"),
        ("quick wins tab",    "renderQuickWins"),
    ],
    "index.html": [
        ("year cards",        "year-card"),
        ("guides present",    "guide"),
        ("shuffle button",    "shuffle-btn"),
        ("gems data",         "all-gems-data"),
    ],
}


def run_node_parse(code: str) -> tuple[bool, str]:
    """Parse JS code with node. Returns (ok, error)."""
    try:
        result = subprocess.run(
            ["node", "-e", "new Function(require('fs').readFileSync(0, 'utf8'))"],
            input=code, capture_output=True, text=True, timeout=15,
        )
        if result.returncode == 0:
            return True, ""
        return False, result.stderr.strip()
    except FileNotFoundError:
        return True, "(node not installed — JS syntax check skipped)"
    except subprocess.TimeoutExpired:
        return False, "node timed out"


def check_file(path: Path, required_substrings: list[tuple[str, str]]) -> tuple[int, int]:
    """Returns (passed, total)."""
    if not path.exists():
        print(f"  ✗ {path.name} — file not found")
        return (0, 1)
    html = path.read_text()
    if not html:
        print(f"  ✗ {path.name} — empty file")
        return (0, 1)
    print(f"  {path.name} ({len(html):,} bytes)")
    passed = 0
    total = 0
    # Substring checks
    for label, needle in required_substrings:
        total += 1
        if needle in html:
            passed += 1
        else:
            print(f"      ✗ missing: {label} (looking for {needle!r})")
    # Script syntax check (combine all <script> blocks of unknown type, skip JSON-ld blocks)
    scripts = re.findall(r'<script(?:\s[^>]*)?>([\s\S]*?)</script>', html)
    for i, script in enumerate(scripts):
        total += 1
        # Skip JSON data scripts
        if script.strip().startswith("[") or script.strip().startswith("{"):
            passed += 1
            continue
        ok, err = run_node_parse(script)
        if ok:
            passed += 1
        else:
            print(f"      ✗ script {i} parse error: {err[:200]}")
    if passed == total:
        print(f"      ✓ {passed}/{total} checks pass")
    else:
        print(f"      ⚠ {passed}/{total} checks pass")
    return (passed, total)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--strict", action="store_true", help="Exit 1 on any failure")
    args = parser.parse_args()

    total_passed = 0
    total_checks = 0

    print("=== Year dashboards ===")
    for year in range(2014, 2026):
        path = PROJECT_ROOT / f"index-{year}.html"
        reqs = [(label, fn(year)) for label, fn in YEAR_DASHBOARD_REQUIREMENTS]
        # Drop the legacy 'right: 70px' check if .badges-row is present (newer layout)
        passed, total = check_file(path, reqs)
        total_passed += passed
        total_checks += total

    print("\n=== Cross-year guides ===")
    for fname, reqs in GUIDE_REQUIREMENTS.items():
        path = PROJECT_ROOT / fname
        passed, total = check_file(path, reqs)
        total_passed += passed
        total_checks += total

    print(f"\n=== Summary: {total_passed}/{total_checks} checks pass ===")
    if total_passed == total_checks:
        print("✓ All validations pass")
        return 0
    failed = total_checks - total_passed
    print(f"✗ {failed} check(s) failed")
    return 1 if args.strict else 0


if __name__ == "__main__":
    sys.exit(main())
