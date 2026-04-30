# Agent Guide

This project uses AI-assisted editorial work, but the repo should stay
agent-neutral. `AGENTS.md` is the canonical instruction file. Tool-specific
entry points, such as `CLAUDE.md`, should point here instead of duplicating
guidance.

## Project

WWDC Journal is a static archive and analysis site for Apple's WWDC sessions
from 2014-2025. It combines generated session metadata with human/agent-curated
analysis: learning pathways, topic clusters, hidden gems, modernization advice,
speaker indexes, and cross-year guides.

The site has no build step and no runtime dependencies. HTML files are the
published artifact.

## Repository Layout

- `index.html` - landing page, cross-year search, guide links, hidden-gem shuffle
- `index-{YEAR}.html` - single-file yearly dashboards
- `modernization.html`, `featured.html`, `marketing.html`, `accessibility.html` - cross-year guides
- `analysis-{YEAR}/` - curated markdown analysis by topic cluster
- `analysis/` - original 2025 analysis kept for compatibility
- `data/wwdc{YEAR}-sessions.json` - generated per-year session metadata
- `data/wwdc{YEAR}-by-topic.json` - generated topic groupings
- `data/wwdc{YEAR}-pathways.json` - curated pathways and dependency data
- `bin/` - mechanical pipeline and validation scripts
- `transcripts/` - local transcript cache, intentionally gitignored

## Ground Rules

- Keep the project static. Do not introduce a framework, package manager, or
  build system without an explicit decision.
- Preserve the single-file dashboard pattern for each `index-{YEAR}.html`.
- Treat `data/wwdc{YEAR}-sessions.json` and `data/wwdc{YEAR}-by-topic.json` as
  mechanically generated from the Nonstrict WWDC index.
- Treat pathway files, markdown analysis, gems, deltas, and guide content as
  editorial artifacts that require judgment.
- Do not commit `transcripts/` or `data/wwdc-index.json`; both are re-fetchable.
- Keep source attribution intact when using transcript or documentation-derived
  material.
- Prefer focused updates over broad visual rewrites. Many pages share patterns,
  but they are intentionally self-contained.

## Validation

Run this before committing dashboard, guide, or landing-page changes:

```bash
bin/validate-dashboards.py --strict
```

Run this before committing changes to Apple documentation URLs:

```bash
bin/check-doc-links.py --strict
```

The GitHub Pages workflow runs dashboard validation before publishing.

## Adding A New WWDC Year

The mechanical pipeline gets the source data into place:

```bash
bin/fetch-transcripts.py 2026
bin/build-metadata.py 2026
```

The editorial pass produces:

- `analysis-2026/`
- `data/wwdc2026-pathways.json`
- `index-2026.html`
- any updates needed in cross-year guides
- a new year card in `index.html`

Use the detailed workflow in `docs/recreating-a-year.md`.

After the editorial pass:

```bash
bin/refresh-gems.py
bin/validate-dashboards.py --strict
```

Commit the new year artifacts and push to `main`; GitHub Pages deploys from
there.

## Editorial Expectations

For transcript and session analysis, optimize for usefulness to Apple-platform
developers rather than exhaustive summaries. Good outputs identify what changed,
why it mattered, what sessions belong together, and what a developer should do
with the information.

When curating pathways:

- Choose a gateway session that orients the learner.
- Order sessions by prerequisite relationship, not by session number.
- Include optional sessions only when they deepen a coherent path.
- Keep descriptions short and specific.

When identifying hidden gems:

- Prefer concrete APIs, migration risks, performance wins, behavioral changes,
  and transcript-only details.
- Avoid re-labeling headline announcements as hidden gems.
- Include session/source identifiers wherever possible.

When updating guides:

- Keep modernization advice actionable.
- Connect recommendations to the WWDC year/session that introduced or clarified
  the practice.
- Preserve localStorage keys unless intentionally migrating user progress.

## Claude Compatibility

Claude Code is a common agent for this repo, but it should not be the only
documented workflow. Keep `CLAUDE.md` as a symlink or short pointer to this file.
Update this file first whenever agent instructions change.
