# bin/ — pipeline scripts

Reusable scripts for the mechanical parts of the pipeline. Anything that
requires judgment (analyzing transcripts, curating pathways, naming gems)
is handled by Claude Code agents — see the project root README and
`~/Documents/CLAUDE_JOURNAL/PERSONAL/2026-04-25-1830-wwdc-journal-recreation-guide.md`.

## Scripts

### `fetch-transcripts.py YEAR [YEAR ...]`
Downloads the Nonstrict zip + master index, extracts transcripts for
specified year(s) into `transcripts/{YEAR}/`. Caches the zip at
`/tmp/wwdc-transcripts.zip` so re-runs are fast.

```bash
bin/fetch-transcripts.py 2026
bin/fetch-transcripts.py 2014-2025          # range
bin/fetch-transcripts.py 2024 2025 --keep-zip
```

### `build-metadata.py YEAR [YEAR ...]`
Builds `data/wwdc{YEAR}-sessions.json` and `data/wwdc{YEAR}-by-topic.json`
from the master index, marking which sessions have transcripts.

```bash
bin/build-metadata.py 2026
bin/build-metadata.py 2014-2025
```

### `refresh-gems.py`
Re-extracts every hidden gem from every year dashboard's `gems` JS array
and rebuilds the inline gem corpus in `index.html` (powering the
"Surprise me" shuffle button). Run after editing gems in year dashboards
or adding a new year.

```bash
bin/refresh-gems.py
```

### `check-doc-links.py [--strict]`
Validates that every Apple documentation link in the cross-year guides
actually resolves to a real page. Apple's developer site serves a
custom 404 page with HTTP 200, so this script does a full GET and
sniffs the body for known soft-404 markers.

```bash
bin/check-doc-links.py                    # show all results
bin/check-doc-links.py --quiet            # only show broken links
bin/check-doc-links.py --strict           # exit 1 on any broken link
bin/check-doc-links.py --output report.json
```

Network-bound (~10s for 100 URLs). Run before commits that touch
`docUrl` values, or include in CI.

### `validate-dashboards.py [--strict]`
Validates every dashboard parses cleanly and contains the expected
features (search, breadcrumb, badges-row, etc.). Use in CI or before
committing.

```bash
bin/validate-dashboards.py            # warnings only
bin/validate-dashboards.py --strict   # exit 1 on any failure
```

## Adding a new year (e.g. WWDC 2026)

```bash
# 1. Fetch + index
bin/fetch-transcripts.py 2026
bin/build-metadata.py 2026

# 2. Hand off to Claude (judgment-heavy work)
#    → Read the recreation guide, then ask Claude to:
#      "Build a complete WWDC 2026 dashboard following the pattern
#       in index-2025.html"
#    → It will produce analysis-2026/, data/wwdc2026-pathways.json,
#      and index-2026.html.

# 3. Refresh shuffle pool + landing page
bin/refresh-gems.py
# (manually edit index.html to add a 2026 year-card; ~5 minutes)

# 4. Validate
bin/validate-dashboards.py --strict

# 5. Commit
git add transcripts/2026 data/wwdc2026-* analysis-2026/ index-2026.html index.html
git commit -m "Add WWDC 2026 dashboard"
```

## What's NOT scripted (and shouldn't be)

These tasks need an LLM with full context to do well:
- Picking the headline themes for a year
- Curating learning pathways and prerequisites
- Identifying genuine "hidden gems" vs ordinary content
- Writing pathway descriptions and dependency graph chains
- Adding new modernization/featured/marketing items
- Crafting urgent-badge reasons
- Comparing transcript content against official DocC

These are agent prompts, not Python scripts. See the recreation guide
for the per-year agent prompt template.
