# Recreating A WWDC Year

This document describes the neutral, agent-assisted workflow for adding a new
WWDC year to WWDC Journal. It separates mechanical data generation from
editorial analysis.

## Inputs

- Nonstrict WWDC Index metadata
- Nonstrict transcript archive
- Apple Developer session pages and documentation
- Existing dashboards, especially the most recent `index-{YEAR}.html`
- Existing pathway and analysis files for nearby years

## Mechanical Setup

Fetch transcripts and build generated metadata:

```bash
bin/fetch-transcripts.py 2026
bin/build-metadata.py 2026
```

This creates or refreshes:

- `transcripts/2026/` locally
- `data/wwdc2026-sessions.json`
- `data/wwdc2026-by-topic.json`

`transcripts/` and `data/wwdc-index.json` are local/generated inputs and should
not be committed.

## Editorial Pass

Use an AI coding agent or manual review to produce the curated layer:

- `analysis-2026/*.md`
- `data/wwdc2026-pathways.json`
- `index-2026.html`
- updates to `index.html`
- updates to cross-year guides when the new year changes modernization,
  accessibility, featured, or marketing advice

The agent should read:

- `AGENTS.md`
- the latest complete dashboard, e.g. `index-2025.html`
- the latest pathway data, e.g. `data/wwdc2025-pathways.json`
- representative analysis files from recent years
- generated 2026 metadata and transcripts

## Suggested Agent Prompt

```text
Read AGENTS.md and docs/recreating-a-year.md.

Build a complete WWDC 2026 dashboard following the existing WWDC Journal
patterns. Use index-2025.html as the closest structural reference, but adapt
the content to 2026.

Produce:
- analysis-2026/ markdown files grouped by major topic cluster
- data/wwdc2026-pathways.json with curated learning pathways, prerequisites,
  clusters, and hidden-gem source references
- index-2026.html as a self-contained yearly dashboard
- any required updates to index.html and cross-year guides

Keep the repo static. Preserve the single-file dashboard pattern. Do not commit
transcripts/ or data/wwdc-index.json. Run bin/validate-dashboards.py --strict
when finished.
```

## Quality Bar

The new year should feel like the existing 2014-2025 dashboards:

- clear yearly theme
- accurate session counts and topic distribution
- searchable session/pathway/gem content
- curated pathways with a coherent learning order
- clusters that reveal related sessions across the same feature area
- hidden gems that are genuinely actionable or easy to miss
- documentation deltas where transcript content clarifies or exceeds official
  documentation

Avoid generic summaries. The value of the project is in connecting sessions,
surfacing practical implications, and helping developers decide what to watch
or adopt.

## Finalization

Refresh the landing-page hidden-gem pool:

```bash
bin/refresh-gems.py
```

Validate:

```bash
bin/validate-dashboards.py --strict
```

If documentation URLs were added or changed:

```bash
bin/check-doc-links.py --strict
```

Commit the curated artifacts:

```bash
git add data/wwdc2026-* analysis-2026/ index-2026.html index.html
git add modernization.html featured.html marketing.html accessibility.html
git commit -m "Add WWDC 2026 dashboard"
```

Only include cross-year guide files that actually changed.
