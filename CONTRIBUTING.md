# Contributing

Thanks for your interest. This repository is a personal toolkit, kept small and high quality, so contributions are reviewed for fit as well as correctness.

## Ways to help

- **Report a bug or a wrong number** using the bug report form under Issues. Include the skill, the input you used and what you expected.
- **Suggest a skill or app** using the feature request form. Describe the job it does and who uses it.
- **Improve an existing skill** with a pull request: clearer instructions, better sources, fixes to scripts or examples.

## Adding a skill

1. Copy [`template/skill-template`](template/skill-template/) to `skills/<your-skill-name>/`.
2. Name the folder in lowercase kebab-case. The folder name must match the `name` field in `SKILL.md`.
3. Fill in `SKILL.md`: a `description` that says what the skill does and when to use it (up to 1,024 characters), plus `license`, and `metadata` with `author`, `version` and `category`.
4. Keep `SKILL.md` under 500 lines. Move long reference material into `references/` and link to it.
5. Put code in `scripts/` and examples or images in `assets/`.
6. Add a `README.md` for humans: what it does, a screenshot, how to use it, limits.
7. Add a row to the catalogue in the root `README.md` and an entry to `CHANGELOG.md`.

## Standards

- **Sources and dates.** Any number in an example carries its as-of date and source.
- **No credentials or personal data** in any file, including examples and screenshots.
- **Education only.** Finance content must not read as personalised advice.
- **Credit and licence.** By contributing you agree your work is released under the Apache License 2.0. Do not remove the credit line or [NOTICE](NOTICE).
- **Commit messages** in the imperative, for example "Add reverse DCF chart to scorecard".

## Pull requests

Keep each pull request to one change. Fill in the pull request template, and describe how you checked the result.
