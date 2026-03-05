# qrine Philosophy

## 1. Predictability Over Convenience

`qrine` is designed for both humans and AI agents, but its core contract is deterministic.

- same input => same output structure
- stable fields in machine-readable output
- explicit exit codes

Human ergonomics can vary. The machine contract should not.

## 2. Raw Payloads Are First-Class

Agents generate structured data better than flat flag strings.
`--input-json` is a primary input path, not a secondary feature.

This avoids translation loss between agent planning and CLI execution.

## 3. Runtime Introspection Beats Stale Docs

Agents should be able to discover command shape at runtime.
`qlint schema` exposes command input/output structure as JSON.

The CLI itself is a queryable source of truth.

## 4. Defense in Depth for Inputs

Agents are fast and often wrong in new ways.
The CLI is the last guardrail before execution.

`qrine` validates input to reject common hallucination patterns:

- control characters
- URL-like fragments inside paths (`?`, `#`, `%`)

Unsafe bypasses are explicit (`--unsafe-paths`).

## 5. Context Window Discipline

Large outputs waste tokens and degrade downstream reasoning.
`qrine` provides controls to constrain output volume and shape:

- `--fields` to project diagnostic fields
- `--max-diagnostics` to cap result size
- `ndjson` for streaming consumption

## 6. Safe Planning Before Execution

`--dry-run` validates inputs and resolves file targets without lint execution.

This supports agent planning loops where validation should happen before costly or broad operations.

## 7. Incremental Extensibility

Agent-safe capabilities should be additive, not a rewrite mandate.

`qrine` keeps compatibility with legacy usage (`qlint <paths>`) while adding agent-first surfaces:

- `lint` command mode
- structured schema output
- deterministic envelopes

The goal is steady evolution with stable contracts.
