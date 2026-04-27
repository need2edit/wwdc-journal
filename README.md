# WWDC Journal

Deep transcript analysis, learning pathways, hidden gems, and developer-doc deltas across **12 years of Apple's Worldwide Developers Conference (2014–2025)**.

- **1,895 sessions** indexed
- **1,751 transcripts** processed
- **166 curated learning pathways**
- **12 interactive year dashboards** + a cross-year modernization dashboard
- **Single-file HTML**: no build step, no dependencies — open in any browser

## Open it

```
open index.html
```

The landing page links to each year's dashboard and to the cross-year modernization guide.

## What's in each year dashboard

- **Hero** with sessions/pathways/topics stats and a search bar
- **Search** with autocomplete across sessions, pathways, gems, and clusters (`/` or `Cmd+K` to focus)
- **Learning Pathways** — curated session sequences with prerequisites and learning order
- **Topic Map** — distribution of sessions across Apple's topic taxonomy
- **Session Clusters** — groups covering the same feature from different angles
- **Hidden Gems & Best Practices** — filterable by category (URGENT, HIDDEN GEM, BEST PRACTICE, PERFORMANCE, DEPRECATION)
- **Docs vs. Transcripts** — what's only in transcripts vs. what's documented
- **Dependency Graph** — visual prerequisite chains between sessions

Click anything (session pill, cluster badge, gem card, graph node) to jump to the WWDC video.

## The Modernization Guide

`modernization.html` — interactive dashboard for bringing a dated project up to speed:

- Pick the year your project was last refreshed; older items are filtered out
- 5-phase migration pathway (Stop the Bleeding → Foundation → Paradigms → Polish → Forward Discipline)
- 60+ checkable modernization items with persistent progress (localStorage)
- Year-by-year deprecation reference
- Cross-year hidden gems

`MODERNIZATION-GUIDE.md` is the long-form markdown version (17 sections + 2 appendices).

## Project layout

```
index.html              # Landing page (12 year cards + link to modernization)
index-{YEAR}.html       # Year dashboards (2014–2025)
modernization.html      # Interactive cross-year modernization guide
MODERNIZATION-GUIDE.md  # Long-form modernization reference

analysis-{YEAR}/        # Deep markdown analyses by topic cluster (per year)
analysis/               # Original 2025 analyses (kept for compatibility)

data/
  wwdc{YEAR}-sessions.json   # Per-year session metadata
  wwdc{YEAR}-by-topic.json   # Sessions grouped by topic
  wwdc{YEAR}-pathways.json   # Curated pathways, prerequisites, clusters
  session-pathways.json      # 2025 pathways (canonical name)

transcripts/{YEAR}/     # Plain-text transcripts (.gitignored — fetch via script below)
```

## Fetching transcripts

Transcripts (~48MB) are gitignored. To regenerate:

```bash
mkdir -p data
curl -sL "https://nonstrict.eu/wwdcindex/transcripts.zip" -o /tmp/wwdc.zip
curl -sL "https://nonstrict.eu/wwdcindex/data.json" -o data/wwdc-index.json

for year in 2014 2015 2016 2017 2018 2019 2020 2021 2022 2023 2024 2025; do
  unzip -o /tmp/wwdc.zip "wwdc${year}/*.en.txt" -d /tmp/extract-${year}/
  mkdir -p transcripts/${year}/
  cp /tmp/extract-${year}/wwdc${year}/*.en.txt transcripts/${year}/ 2>/dev/null
done
rm -rf /tmp/wwdc.zip /tmp/extract-*
```

Source attribution: transcripts come from [Nonstrict WWDC Index](https://nonstrict.eu/wwdcindex/) and (for richer 2025 markdown) [auramagi's gist](https://gist.github.com/auramagi/9c040c2233dfe71c24c76942e186f788).

## Adding a new year (e.g., when WWDC 2026 drops)

The full recreation pipeline is documented in `~/Documents/CLAUDE_JOURNAL/PERSONAL/2026-04-25-1830-wwdc-journal-recreation-guide.md`. In short:

1. Fetch transcripts for the new year (script above)
2. Build per-year metadata JSONs
3. Launch a per-year analysis agent (one comprehensive Claude sub-agent that reads transcripts, writes analyses, generates pathways JSON, and produces the dashboard HTML using `index-2025.html` as the template)
4. Add a card to `index.html` for the new year
5. Add the new year to `modernization.html`'s year picker
