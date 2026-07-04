# Campaign: docs-search
Goal: Add client-side full-text search to the documentation site with a keyboard-driven UI.
Status: phase 2 of 3 — index pipeline merged; UI and highlighting in flight.

## Phases

### Phase 1 — Index pipeline (done)
- [x] Build-time indexer emitting `search-index.json` — worker: codex — verify: `npm run build && node scripts/check-index.mjs`
- [x] Tokenizer handling code identifiers (camelCase, snake_case) — worker: codex — verify: `npm test -- tokenizer`

### Phase 2 — Search UI
- [x] Query engine with ranking (title > heading > body) — worker: codex — verify: `npm test -- ranking`
- [ ] Search palette component (Cmd-K, keyboard navigation) — worker: opus — verify: `npm test -- palette` + visual review
- [ ] Result highlighting and deep links to headings — worker: codex — verify: `npm test -- highlight`

### Phase 3 — Integration
- [ ] Merge phase-2 branches, wire palette to engine — worker: opus (integration) — verify: `npm test && npm run e2e`
- [ ] Index size budget check in CI (< 250 KB gzipped) — worker: codex — verify: CI green on PR

## Fleet (active dispatches)
| Task | Worker | Branch | Worktree | Status |
|---|---|---|---|---|
| Search palette | opus | campaign/palette | ../wt-palette | in progress |
| Result highlighting | codex | campaign/highlight | ../wt-highlight | dispatched 14:05 |
| Ranking engine | codex | campaign/ranking | — | merged, verified, worktree removed |
