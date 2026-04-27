#!/usr/bin/env python3
"""
Build per-year metadata JSON files from the master Nonstrict WWDC index.

For each year specified, produces:
- data/wwdc{YEAR}-sessions.json — full session metadata
- data/wwdc{YEAR}-by-topic.json — sessions grouped by Apple's topic taxonomy

Each session entry includes a `has_transcript` boolean computed from
transcripts/{YEAR}/{eventContentId}.en.txt existence.

Usage:
    bin/build-metadata.py 2026
    bin/build-metadata.py 2014-2025
"""
import argparse
import json
import os
import sys
from collections import Counter
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.resolve()
DATA_DIR = PROJECT_ROOT / "data"
TRANSCRIPTS_DIR = PROJECT_ROOT / "transcripts"
INDEX_PATH = DATA_DIR / "wwdc-index.json"


def parse_years(args: list[str]) -> list[int]:
    years: set[int] = set()
    for arg in args:
        if "-" in arg:
            start, end = map(int, arg.split("-"))
            years.update(range(start, end + 1))
        else:
            years.add(int(arg))
    return sorted(years)


def build_year(master: dict, year: int) -> dict:
    """Returns summary dict with stats for the year."""
    sessions = [s for s in master["sessions"] if s.get("year") == year]
    transcript_dir = TRANSCRIPTS_DIR / str(year)
    transcript_ids: set[str] = set()
    if transcript_dir.exists():
        # Accept either .en.txt (Nonstrict) or *(WWDCxx-NNN).md (auramagi gist)
        for fname in os.listdir(transcript_dir):
            if fname.endswith(".en.txt"):
                transcript_ids.add(fname[:-len(".en.txt")])
            else:
                # Look for trailing (WWDCxx-NNN) pattern in markdown filenames
                import re
                m = re.search(r"\(WWDC\d{2}-(\d+)\)\.md$", fname)
                if m:
                    transcript_ids.add(m.group(1))

    by_topic: dict[str, list] = {}
    for s in sessions:
        topic = s.get("topic", "Unknown")
        sid = s.get("eventContentId", "")
        entry = {
            "session_id": sid,
            "title": s.get("title", ""),
            "description": s.get("description", ""),
            "topic": topic,
            "platforms": s.get("platforms", []),
            "speakers": s.get("speakers", []),
            "apple_url": s.get("appleWeblink", ""),
            "has_transcript": sid in transcript_ids,
        }
        by_topic.setdefault(topic, []).append(entry)

    sessions_path = DATA_DIR / f"wwdc{year}-sessions.json"
    by_topic_path = DATA_DIR / f"wwdc{year}-by-topic.json"
    with open(sessions_path, "w") as f:
        json.dump(sessions, f, indent=2)
    with open(by_topic_path, "w") as f:
        json.dump(by_topic, f, indent=2)

    matched = sum(1 for s in sessions if s.get("eventContentId") in transcript_ids)
    topic_counts = Counter(s.get("topic", "Unknown") for s in sessions)
    return {
        "year": year,
        "sessions": len(sessions),
        "matched_transcripts": matched,
        "topics": len(topic_counts),
        "top_topics": topic_counts.most_common(5),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("years", nargs="+", help="Year(s) or range, e.g. 2026 or 2014-2025")
    args = parser.parse_args()

    if not INDEX_PATH.exists():
        print(f"Master index not found at {INDEX_PATH}", file=sys.stderr)
        print("Run bin/fetch-transcripts.py first.", file=sys.stderr)
        return 1

    print(f"→ Loading master index ({INDEX_PATH.stat().st_size // 1024} KB)")
    with open(INDEX_PATH) as f:
        master = json.load(f)
    print(f"  {len(master.get('sessions', []))} sessions across all years")
    print()

    years = parse_years(args.years)
    summaries = []
    for year in years:
        summary = build_year(master, year)
        summaries.append(summary)
        print(f"WWDC {summary['year']}: {summary['sessions']} sessions, "
              f"{summary['matched_transcripts']} matched transcripts, "
              f"{summary['topics']} topics")
        for topic, count in summary["top_topics"]:
            print(f"    {topic}: {count}")

    print("\n✓ Done")
    return 0


if __name__ == "__main__":
    sys.exit(main())
