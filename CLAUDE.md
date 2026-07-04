# Repository guide

Claude Code skills for multi-agent orchestration. Each skill lives at
`skills/<name>/SKILL.md` with optional `scripts/`, `references/`, and
`assets/` directories, per the [Agent Skills spec](https://agentskills.io/specification).

## Working on this repo

- Run `python3 scripts/validate.py` after editing any SKILL.md. CI runs the
  same script.
- Keep each SKILL.md under 500 lines. Add `references/` files only when
  content outgrows the main file.
- Improve skills by replacing or tightening existing text. Appending grows
  load cost for every future invocation.
- Keep content machine-agnostic: no personal paths, account names, emails, or
  references to private tooling.
- Update `examples/` when a skill's file formats change; the examples must
  match what the skill actually produces.

## Writing style

- Direct statements and imperatives. Every sentence carries information.
- No slogans or slogan-like phrasing.
- No rhetorical contrast structures ("it's not X, it's Y" / "X, not Y").
- No snark, sales language, defensive language, or obvious caveats.
- State the reason behind a rule when it's not evident; omit it when it is.
