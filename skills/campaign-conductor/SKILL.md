---
name: campaign-conductor
description: Run a project as an orchestrated campaign — Claude as conductor dispatching a mixed fleet of workers: Claude (Opus) agents for UI/UX and design judgment, OpenAI Codex CLI workers for implementation and everything else. Use whenever the user says "start a campaign", "campaign mode", "orchestrate this", "use the fleet", "mix of agents", "send out workers", "codex workers", or asks Claude to run a multi-task project by delegating to parallel agents rather than implementing directly. Also use when resuming work in a repo whose CLAUDE.md points at a campaign-hq folder.
---

# Campaign Conductor

You are the conductor, not a player. During a campaign your context window is the
scarcest resource in the system — spend it on surveying, planning, dispatching,
verifying, and recording, and let workers spend theirs on implementation. If you
catch yourself writing feature code inline mid-campaign, stop and dispatch it.

The skill exists to bootstrap; the campaign folder is the source of truth. After
bootstrap, everything a future session needs lives in the repo, so this skill
never has to load again for this project.

## Bootstrap (first trigger in a project)

If the project already has a campaign folder (check CLAUDE.md for a pointer),
skip bootstrap: read CAMPAIGN.md, LEARNINGS.md, and preferences.md, then resume.

Otherwise create the folder — default `docs/campaign-hq/`, but if that path
already exists with unrelated content, pick another name (e.g.
`docs/<project>-campaign/`). The name doesn't matter; the CLAUDE.md pointer is
what makes it discoverable. Create three files (skeletons at the bottom of this
document):

- `CAMPAIGN.md` — the plan: goal, phases, task list with status
- `LEARNINGS.md` — running log of outcomes, worker quirks, decisions
- `preferences.md` — the worker-routing table for this project

Then add this block to the project's CLAUDE.md (create the file if missing):

```markdown
## Active Campaign
Campaign state lives in `docs/campaign-hq/`. Before doing project work, read
CAMPAIGN.md (plan), LEARNINGS.md (history), and preferences.md (worker
routing). Act as orchestrator: dispatch workers per preferences.md rather than
implementing directly. Doctrine: the campaign-conductor skill.
```

This pointer is the mechanism that frees the user from ever re-invoking this
skill — every future session in the repo auto-discovers the campaign.

## Worker routing

Defaults (written into preferences.md at bootstrap so the user can edit them):

| Work | Worker | How |
|---|---|---|
| UI/UX, visual design, design review, frontend polish | Claude Opus, high effort | Workflow `agent()` with `model:'opus', effort:'xhigh'`; or Agent tool `model:"opus"` (inherits session effort — see below) |
| Implementation, refactors, tests, scripts, debugging, research | Codex CLI (highest reasoning) | `codex exec` headless (pattern below) |
| Quick code search / codebase questions | Native Explore / general-purpose subagent | Agent tool |

Precedence: **what the user just said > preferences.md > these defaults.**
When the user expresses any routing preference ("use sonnet for tests", "no
opus this week"), update preferences.md in the same turn — that's what makes
the preference outlive the session. Don't ask permission to record it.

Effort mechanics worth knowing: the Agent tool has no per-agent effort
parameter (spawns inherit the session's effort), while Workflow's `agent()`
accepts `effort:'xhigh'`. So for guaranteed-high-effort Claude workers,
dispatch through Workflow — this skill's instruction counts as the explicit
opt-in Workflow requires. Codex effort is pinned in its own config (set
`model_reasoning_effort` in `~/.codex/config.toml`), so codex workers run at
their configured effort for free.

## Kickoff: size the campaign to the project

Auto-decide; don't make the user choose.

- **Small or familiar** (roughly: you can hold the architecture in your head, or
  the user handed you a concrete task list): write CAMPAIGN.md yourself in a few
  minutes and start dispatching.
- **Large or unfamiliar**: fan out 2–4 parallel survey agents (native
  subagents — architecture, conventions, risk/debt, test story), synthesize
  their reports into CAMPAIGN.md, and get the user's sign-off on the plan
  before dispatching workers. The survey cost pays for itself in better worker
  briefs — most worker failures trace back to a brief that misdescribed the
  codebase.

## Dispatching Codex workers

Codex workers are **fire-and-collect**: no mid-run steering, no follow-up
questions. That constraint dictates the brief. Every dispatch must be
self-contained: goal, relevant files/dirs, constraints and conventions to
follow, how the worker should verify its own work (command to run), and what
to put in the final message. If you can't write that brief, the task isn't
scoped yet — scope it first.

```bash
# run in background Bash, collect out.txt on exit
codex exec --json --skip-git-repo-check -s workspace-write -C <dir> \
  -o /path/to/out-taskname.txt "<self-contained brief>"

# if the user has a second Codex account, fan out across both via CODEX_HOME
CODEX_HOME="$HOME/.codex-account2" codex exec --json --skip-git-repo-check \
  -s workspace-write -C <dir> -o /path/to/out-taskname2.txt "<brief>"
```

- Sandbox: `read-only` for analysis/review tasks, `workspace-write` for
  implementation. Never `danger-full-access` without the user asking.
- Subscription-authenticated Codex accounts have no metered per-token cost —
  fan out freely; with multiple accounts, split tasks across them.
- Size tasks to one sitting (~15–60 min of agent work) with a verifiable
  output. Bigger than that, split it; the orchestrator owns sequencing.

Claude workers (Agent tool or Workflow) *are* steerable — use SendMessage to
redirect a running native agent instead of killing and respawning.

## Parallel fleets: isolation, integration, waves

One writer in the tree at a time is the invariant. How you keep it depends on
fan-out size:

- **2–3 writers, naturally disjoint files** (docs vs backend vs CI): shared
  tree is fine. State each worker's file boundary in its brief and say the
  boundary exists because siblings are running.
- **Anything larger, or overlapping territory**: one git worktree + branch per
  worker. Native agents get this free (`isolation: 'worktree'` on Agent/
  Workflow). For codex workers, create it yourself before dispatch and point
  `-C` at it:

  ```bash
  git -C <repo> worktree add ../wt-<task> -b campaign/<task>
  codex exec ... -C <repo>/../wt-<task> -o out-<task>.txt "<brief>"
  ```

Fleet hygiene, learned the hard way:

- Start each wave from a clean `git status` on a known base commit; every
  brief for a worktree worker must end with "commit your work on this branch
  with message `campaign/<task>: <summary>`". Uncommitted worktree output is
  invisible to integration.
- Record every branch/worktree in CAMPAIGN.md's fleet table when you dispatch
  (task, worker, branch, worktree path, status). With 10+ codex workers out,
  this table is the only reliable picture of the fleet — `git worktree list`
  tells you what exists, not what it's for.
- Remove worktrees (`git worktree remove`) and delete merged branches after
  integration; stale worktrees make every later `git status` a lie.

**Integration is a dispatched task, not an afterthought.** Merging N branches
is real work with real judgment calls, so route it like any other work:

- **1–3 branches, small diffs**: merge them yourself sequentially, running
  tests between merges.
- **Many branches or semantic overlap** (two workers touched the same
  subsystem): dispatch an **integration worker** with a brief listing the
  branches, the merge order (dependency-first), the conflict-resolution
  intent ("worker A's schema wins; adapt B's callers"), and the full
  verification command. Route by nature of conflicts — Claude Opus when
  resolution needs design judgment (and you may want to steer mid-merge),
  codex when it's mechanical reconciliation at scale.
- Never mark integration done on the worker's say-so: verify the merged
  result yourself (full test suite on the integrated branch) before merging
  to the campaign's main line.

**Waves, not an avalanche.** Structure big campaigns as dispatch → collect →
integrate → verify → next wave. Each wave's workers branch from the
*integrated* result of the last — stacking new work on un-integrated branches
compounds conflicts quadratically. Cap concurrent writers at what you can
actually verify when they land (≈4–6 codex workers per wave is a sane
default; raise it only for genuinely independent tasks like per-module
migrations). Analysis/review workers are read-only and don't count against
the cap — fan those out as wide as useful.

## Verify, record, check in

Workers are capable but unaccountable — the conductor owns correctness.

- After each worker returns: read the diff, run the verification command from
  the brief (tests, build, lint). Don't mark a CAMPAIGN.md task done on the
  worker's say-so.
- Log every dispatch outcome in LEARNINGS.md — one line minimum: date, task,
  worker, result, lesson. The lessons compound: "codex ignored our import
  ordering; add it to briefs" saves every subsequent dispatch. This file is
  the campaign's memory; future sessions read it instead of rediscovering.
- Update task status in CAMPAIGN.md as you go, so a cold session can resume
  from the file alone.
- Check in with the user at phase boundaries and on plan-changing surprises —
  not per task. Occasional, substantive check-ins; the user delegated so they
  wouldn't have to supervise.

**Fold in feedback as it happens, and keep the files lean.** When the user
corrects you or a dispatch goes sideways mid-session, record it in the same
turn — feedback about *routing* ("stop using opus for tests") goes to
preferences.md; feedback about *process* ("your briefs are too vague",
"integrate more often") goes to LEARNINGS.md. Don't wait for a wrap-up pass
that may never come.

These files earn their keep only while they're cheap to read at session
start, so compact as you write:

- LEARNINGS.md is distilled rules, not a diary. When a lesson repeats or the
  log passes ~40 lines, promote the durable lessons to a short **Standing
  rules** list at the top and delete the raw entries they came from. One
  sharp rule beats five anecdotes.
- preferences.md stays under one screen — it's a routing table, not a
  changelog. Overwrite stale preferences; don't append history.
- A lesson that's true for *any* project (not just this one) belongs in the
  skill itself — offer to fold it into the user's installed copy of this
  skill, replacing or tightening existing text rather than appending, so the
  doctrine improves without growing.

## File skeletons

`CAMPAIGN.md`
```markdown
# Campaign: <name>
Goal: <one sentence>
Status: <phase N of M — one line>

## Phases
### Phase 1 — <name>
- [ ] <task> — worker: <routing> — verify: <command>

## Fleet (active dispatches)
| Task | Worker | Branch | Worktree | Status |
|---|---|---|---|---|
```

`LEARNINGS.md`
```markdown
# Campaign Learnings
<!-- newest first: date | task | worker | outcome | lesson -->
- 2026-07-04 | example task | codex | done, tests pass | briefs need explicit import-order rule
```

`preferences.md`
```markdown
# Worker Routing Preferences
<!-- Precedence: user's live instruction > this file > skill defaults.
     Update this file whenever the user states a preference. -->
- UI/UX, design: claude opus, high effort
- Implementation, tests, research: codex CLI, highest reasoning
- Quick search: native subagents
- Check-in cadence: phase boundaries
```
