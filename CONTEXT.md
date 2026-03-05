# qrine Agent Context

This CLI is frequently used by AI/LLM agents.
Assume inputs may be malformed or hallucinated.

## Invariants

- Prefer `--output json` or `--output ndjson` for machine parsing.
- Use `qrine schema` before constructing complex payloads.
- Prefer `--input-json` for structured invocation.
- Use `--dry-run` before broad directory scans.
- Use `--fields` and `--max-diagnostics` to reduce token usage.

## Path Safety

Default validation rejects:

- control characters
- `?`, `#`, `%` in paths

Only use `--unsafe-paths` when intentionally required.

## NDJSON Guidance

`--output ndjson` emits independent JSON objects.
Record types:

- `diagnostic`
- `error`
- `summary`
- `plan` (dry-run only)

Process incrementally; do not assume a single top-level array.
