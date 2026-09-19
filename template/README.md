# Template

Start a new skill by copying [`skill-template`](skill-template/) to `skills/<your-skill-name>/`, then follow [CONTRIBUTING.md](../CONTRIBUTING.md).

Rules that make a skill valid under the [Agent Skills specification](https://agentskills.io/specification):

- The folder name is lowercase kebab-case and matches the `name` field.
- `description` is up to 1,024 characters and says both what the skill does and when to use it.
- `SKILL.md` stays under 500 lines. Longer material goes in `references/`, linked one level deep.
