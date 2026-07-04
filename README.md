# A Fable of Codexes

Claude Code skills for orchestrating a **mixed fleet of AI workers** — Claude
as the conductor, dispatching Claude (Opus) agents for design judgment and
OpenAI Codex CLI workers for implementation, in parallel, with git-worktree
isolation and wave-based integration.

## Skills

### campaign-conductor

Turns Claude into a project orchestrator rather than an implementer. On first
use in a repo it bootstraps a `docs/campaign-hq/` folder (plan, learnings,
worker-routing preferences) and adds a pointer to the project's CLAUDE.md — so
every future session auto-discovers the campaign without the skill ever
loading again.

What it encodes:

- **Conductor doctrine** — Claude surveys, plans, dispatches, verifies, and
  records; workers implement. Context is spent on orchestration, not code.
- **Worker routing** — Opus for UI/UX and design judgment, Codex CLI workers
  for implementation/tests/research, native subagents for quick searches.
  Defaults live in an editable `preferences.md`; user overrides persist.
- **Campaign sizing** — small projects get a lightweight plan; large or
  unfamiliar ones get a parallel survey fan-out that writes the plan first.
- **Parallel fleets** — one-writer-per-tree invariant, git worktree + branch
  per worker, a fleet-tracking table, and dedicated *integration workers* to
  merge parallel output. Big campaigns run as waves: dispatch → collect →
  integrate → verify → repeat.
- **Compounding memory** — every dispatch outcome and piece of user feedback
  is logged, then periodically compacted into standing rules so the files
  stay cheap to read.

## Install

Official installer:

```bash
npx skills add <your-gh-org>/a-fable-of-codexes --skill campaign-conductor
```

Manual:

```bash
git clone --depth 1 https://github.com/<your-gh-org>/a-fable-of-codexes.git /tmp/afoc
cp -r /tmp/afoc/skills/campaign-conductor ~/.claude/skills/
```

## Requirements

- **Claude Code** (the skill uses the Agent and Workflow tools).
- **OpenAI Codex CLI** (`codex`), authenticated — a ChatGPT subscription login
  gives flat-rate workers, which is what makes wide fan-out economical. The
  skill degrades gracefully without it: routing just falls back to Claude
  agents for everything.

## Customization

The skill's defaults (Opus for design, Codex for the rest) are starting
points, not doctrine. Tell your Claude your preferences in plain language —
"use Sonnet for tests", "no Codex on this repo" — and it records them in the
project's `preferences.md`, where they persist across sessions.

## License

MIT
