# CLAUDE.md

Guidance for Claude working in this repository.

## What this is

**Foundry** is Jaz's (Jay Nair, GitHub `jay-nair-builds`) public build space: Claude skills, apps and tools that turn ideas into solutions people use. Positioning is builder and technologist, people first. Keep everything professional, finished and useful. Nothing half-built goes in the catalogue.

## Layout

```
foundry/
  skills/      Agent Skills, one folder each (kebab-case)
  apps/        Apps and software (create when the first app ships)
  template/    skill-template/ to copy for new skills
  .github/     Issue forms and PR template
  README.md, CHANGELOG.md, CONTRIBUTING.md, CITATION.cff, NOTICE, LICENSE (Apache-2.0)
```

Structure is type first (`skills/`, `apps/`). The theme is metadata (`category` in SKILL.md, "Theme" column in the README catalogue), never a folder.

## Adding a skill

Follow `CONTRIBUTING.md`. In short: copy `template/skill-template` to `skills/<name>/`, folder name equals `name` in SKILL.md, description up to 1,024 characters saying what it does and when to use it, SKILL.md under 500 lines, code in `scripts/`, longer docs in `references/`, examples in `assets/`, a human `README.md`, then add a catalogue row in the root README and an entry in `CHANGELOG.md`.

## Adding an app

Create `apps/<name>/` with its own README (what it does, how to run it, limits) and the same catalogue row and changelog entry. Keep dependencies minimal and pinned.

## Standards

- **Credit line stays.** Deliverables from the stock-etf-analysis skill carry: "Brand-to-Balance-Sheet (BBS) method by Jay Nair · github.com/jay-nair-builds/foundry". Never remove it or `NOTICE`.
- **Education only.** Finance content is analysis and trade-offs, never personalised advice or buy/sell instructions.
- **Sources and dates.** Every figure in an example carries its source and as-of date.
- **No secrets or personal data** in any file, example or screenshot. Never commit tokens, keys or `.env` files.
- **Style.** Concise, structured, scannable. Bold, business-connected language; no filler or jargon padding. Numbers in tables.
- **Versioning.** Semantic versions. Bump `version` in SKILL.md metadata, `CITATION.cff` and `CHANGELOG.md` together.

## Working with git

- Commit messages in the imperative: "Add reverse DCF chart to scorecard". One change per commit.
- Commit locally when asked. Jaz pushes with GitHub Desktop, so do not push, force-push or rewrite history unless told to.
- Never delete files or folders without saying exactly what will go.
- Default branch is `main`. Use a branch and pull request for larger changes.

## Before finishing a change

1. Check that links, folder names and the `name` field agree.
2. Update the README catalogue and `CHANGELOG.md` if something user-facing changed.
3. Re-run any script or model you touched (`skills/stock-etf-analysis/scripts/engine.py` needs Python 3 with `openpyxl`) and confirm no errors.
4. Tell Jaz what changed in one or two sentences.
