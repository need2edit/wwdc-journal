#!/usr/bin/env python3
"""
Validate that every Apple documentation link in the cross-year guides
actually resolves to a real page (not Apple's soft-404 "Page Not Found").

Apple's developer site serves a custom 404 page with HTTP 200, so naive
HEAD/status-code checks miss broken Help-center URLs. This script does a
full GET and sniffs the body for Apple's known 404 markers.

Usage:
    bin/check-doc-links.py
    bin/check-doc-links.py --strict        # exit 1 on any failure
    bin/check-doc-links.py --files modernization.html featured.html
    bin/check-doc-links.py --workers 30    # default 15
    bin/check-doc-links.py --output report.json
"""
import argparse
import json
import re
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

PROJECT_ROOT = Path(__file__).parent.parent.resolve()
DEFAULT_FILES = ["modernization.html", "featured.html", "marketing.html"]
SOFT_404_MARKERS = (
    "Page Not Found",
    "page you\u2019re looking for can\u2019t be found",
    "page you're looking for can't be found",
)


def extract_doc_urls(path: Path) -> list[str]:
    if not path.exists():
        return []
    html = path.read_text()
    return re.findall(r'docUrl\s*:\s*"([^"]+)"', html)


def check_url(url: str, timeout: float = 12.0) -> tuple[str, str, str]:
    """Returns (url, status, detail)."""
    req = Request(url, headers={"User-Agent": "Mozilla/5.0 (WWDCJournal link checker)"})
    try:
        with urlopen(req, timeout=timeout) as r:
            body = r.read().decode("utf-8", errors="replace")
            for marker in SOFT_404_MARKERS:
                if marker in body:
                    return url, "SOFT404", f"Apple soft-404 ({marker!r} found in body)"
            return url, "OK", f"HTTP {r.status}"
    except HTTPError as e:
        return url, str(e.code), f"HTTPError {e.code}"
    except Exception as e:
        return url, "ERR", f"{type(e).__name__}: {e}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--files", nargs="+", default=DEFAULT_FILES,
                        help="HTML files to scan (default: %(default)s)")
    parser.add_argument("--strict", action="store_true",
                        help="Exit 1 on any broken link")
    parser.add_argument("--workers", type=int, default=15,
                        help="Concurrent HTTP workers (default: %(default)s)")
    parser.add_argument("--output", type=Path,
                        help="Write JSON report to this path")
    parser.add_argument("--quiet", action="store_true",
                        help="Only show broken links")
    args = parser.parse_args()

    # Map url -> set of files where it appears
    url_files: dict[str, set[str]] = {}
    for fname in args.files:
        path = PROJECT_ROOT / fname
        for url in extract_doc_urls(path):
            url_files.setdefault(url, set()).add(fname)

    if not url_files:
        print(f"No docUrl values found in {args.files}", file=sys.stderr)
        return 0

    print(f"Checking {len(url_files)} unique URLs across {len(args.files)} files "
          f"({args.workers} concurrent workers)...")
    print()

    results = []
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futures = {ex.submit(check_url, url): url for url in url_files}
        for fut in as_completed(futures):
            url, status, detail = fut.result()
            results.append({"url": url, "status": status, "detail": detail,
                            "files": sorted(url_files[url])})

    results.sort(key=lambda r: (r["status"] != "OK", r["url"]))
    broken = [r for r in results if r["status"] != "OK"]

    if not args.quiet:
        for r in results:
            mark = "✓" if r["status"] == "OK" else "✗"
            print(f"  {mark} [{r['status']:>7}] {r['url']}")

    print()
    print(f"=== Summary: {len(results) - len(broken)}/{len(results)} OK ===")
    if broken:
        print(f"\n{len(broken)} broken link(s):")
        for r in broken:
            files = ", ".join(r["files"])
            print(f"  ✗ {r['url']}")
            print(f"      [{r['status']}] {r['detail']}")
            print(f"      in: {files}")

    if args.output:
        args.output.write_text(json.dumps({
            "total": len(results),
            "ok": len(results) - len(broken),
            "broken": len(broken),
            "results": results,
        }, indent=2))
        print(f"\nWrote report to {args.output}")

    if broken and args.strict:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
