#!/usr/bin/env python3
"""
Fetch WWDC transcripts for one or more years from the Nonstrict WWDC Index.

Usage:
    bin/fetch-transcripts.py 2026
    bin/fetch-transcripts.py 2025 2026
    bin/fetch-transcripts.py 2014-2025

Downloads the Nonstrict zip (~120MB, cached at /tmp/wwdc-transcripts.zip),
extracts the requested years' .en.txt transcripts into transcripts/{YEAR}/,
and downloads the master index JSON to data/wwdc-index.json if missing.
"""
import argparse
import os
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.resolve()
TRANSCRIPTS_DIR = PROJECT_ROOT / "transcripts"
DATA_DIR = PROJECT_ROOT / "data"
NONSTRICT_ZIP_URL = "https://nonstrict.eu/wwdcindex/transcripts.zip"
NONSTRICT_INDEX_URL = "https://nonstrict.eu/wwdcindex/data.json"
ZIP_CACHE = Path("/tmp/wwdc-transcripts.zip")


def parse_years(args: list[str]) -> list[int]:
    years: set[int] = set()
    for arg in args:
        if "-" in arg:
            start, end = map(int, arg.split("-"))
            years.update(range(start, end + 1))
        else:
            years.add(int(arg))
    return sorted(years)


def download(url: str, dest: Path) -> None:
    print(f"  Downloading {url} -> {dest}")
    subprocess.run(["curl", "-sL", url, "-o", str(dest)], check=True)
    if not dest.exists() or dest.stat().st_size == 0:
        raise RuntimeError(f"Download failed: {dest}")


def ensure_index() -> None:
    index_path = DATA_DIR / "wwdc-index.json"
    if not index_path.exists():
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        download(NONSTRICT_INDEX_URL, index_path)
    else:
        size_mb = index_path.stat().st_size / 1024 / 1024
        print(f"  Index exists ({size_mb:.1f} MB)")


def ensure_zip() -> None:
    if not ZIP_CACHE.exists():
        download(NONSTRICT_ZIP_URL, ZIP_CACHE)
    else:
        size_mb = ZIP_CACHE.stat().st_size / 1024 / 1024
        print(f"  Zip cached at {ZIP_CACHE} ({size_mb:.1f} MB)")


def extract_year(year: int) -> int:
    """Extract year's transcripts from the zip. Returns count."""
    out_dir = TRANSCRIPTS_DIR / str(year)
    out_dir.mkdir(parents=True, exist_ok=True)
    prefix = f"wwdc{year}/"
    count = 0
    with zipfile.ZipFile(ZIP_CACHE) as zf:
        for name in zf.namelist():
            if name.startswith(prefix) and name.endswith(".en.txt"):
                target = out_dir / Path(name).name
                with zf.open(name) as src, open(target, "wb") as dst:
                    shutil.copyfileobj(src, dst)
                count += 1
    return count


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("years", nargs="+", help="Year(s) or range, e.g. 2026 or 2014-2025")
    parser.add_argument("--keep-zip", action="store_true", help="Keep cached zip after run")
    args = parser.parse_args()

    years = parse_years(args.years)
    print(f"Years to fetch: {years}")
    print()

    print("→ Ensuring master index JSON")
    ensure_index()
    print()

    print("→ Ensuring transcripts zip")
    ensure_zip()
    print()

    for year in years:
        print(f"→ Extracting WWDC {year}")
        count = extract_year(year)
        print(f"  {count} transcripts extracted to transcripts/{year}/")
    print()

    if not args.keep_zip and ZIP_CACHE.exists():
        ZIP_CACHE.unlink()
        print(f"  Removed cached zip {ZIP_CACHE} (use --keep-zip to retain)")

    print("\n✓ Done")
    return 0


if __name__ == "__main__":
    sys.exit(main())
