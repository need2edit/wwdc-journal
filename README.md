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

## License

Code in this repository is licensed under the [MIT License](LICENSE).

Original editorial content and curation are licensed under [Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 International](CONTENT-LICENSE.md).

These licenses apply only to original material created for WWDC Journal. They do not apply to Apple-owned content, WWDC session materials, Apple documentation, Apple trademarks, third-party transcript sources, or factual session metadata. See [Third-Party Notices](THIRD_PARTY_NOTICES.md).

## Adding a new year (e.g., when WWDC 2026 drops)

```bash
# 1. Mechanical: fetch transcripts + build per-year metadata
bin/fetch-transcripts.py 2026
bin/build-metadata.py 2026

# 2. Run the agent-assisted editorial pass:
#    Read AGENTS.md and docs/recreating-a-year.md, then build a complete
#    WWDC 2026 dashboard following the index-2025.html pattern. This produces
#    analysis-2026/, data/wwdc2026-pathways.json, and index-2026.html.

# 3. Mechanical: refresh shuffle-button gem pool + validate
bin/refresh-gems.py
bin/validate-dashboards.py --strict

# 4. Hand-edit index.html to add a 2026 year-card (~5 minutes)

# 5. Commit + push (auto-deploys via GitHub Pages)
git add transcripts/2026 data/wwdc2026-* analysis-2026/ index-2026.html index.html
git commit -m "Add WWDC 2026 dashboard"
git push
```

Full recreation pipeline documented in `docs/recreating-a-year.md`.

## Pipeline scripts (`bin/`)

The mechanical parts of the pipeline are scripted; judgment-heavy parts
(curating pathways, identifying hidden gems, writing analyses) are left
to an AI-assisted editorial pass. Agent instructions live in `AGENTS.md`.

- `bin/fetch-transcripts.py` — pull transcripts from Nonstrict
- `bin/build-metadata.py` — derive per-year session JSONs
- `bin/refresh-gems.py` — rebuild the shuffle-button gem pool
- `bin/validate-dashboards.py` — verify HTML/JS integrity

See `bin/README.md` for details and the scripted-vs-editorial split.

## Deployment (GitHub Pages)

A workflow at `.github/workflows/pages.yml` auto-deploys the site on
every push to `main`. To enable:

1. Push the repo to GitHub
2. Repo Settings → Pages → Source: **GitHub Actions**
3. The next push triggers a build at `https://{user}.github.io/{repo}/`

The workflow validates all dashboards before publishing and excludes
the gitignored heavy assets (transcripts, master index).

For other deploy targets:
- **Netlify / Cloudflare Pages**: drag-and-drop the project root (excluding `transcripts/` and `data/wwdc-index.json`)
- **Local only**: `open index.html` (no setup needed)
