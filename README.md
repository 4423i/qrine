# qrine

`qrine` is a static analysis CLI for kdb+/q scripts (`.q`, `.k`).

The current design is **agent-friendly by default**:

- deterministic machine-readable output (`--output json|ndjson`)
- raw JSON request payloads (`--input-json`)
- runtime schema introspection (`qrine schema`)
- defensive input validation against agent hallucinations
- `--dry-run` planning mode

## Why This Design

Human-first CLIs optimize for convenience.
Agent-first CLIs optimize for predictability, introspection, and safety.

`qrine` keeps simple human usage, but promotes stable interfaces for AI agents.

## Core Commands

Lint (legacy-compatible):

```bash
./qrine trade.q
```

Explicit lint command:

```bash
./qrine lint trade.q
```

Directory lint:

```bash
./qrine lint src/
```

Dry run (validate + plan only):

```bash
./qrine lint src/ --dry-run
```

Runtime schema introspection:

```bash
./qrine schema
./qrine schema lint.input
./qrine schema lint.output
```

## Agent-Oriented Input

Raw payload input (no custom flag translation required):

```bash
./qrine lint --input-json '{
  "paths": ["src"],
  "output": "json",
  "fields": ["file", "line", "severity", "message"],
  "max_diagnostics": 50,
  "dry_run": false
}'
```

Supported payload keys:

- `paths`: `string[]`
- `output`: `text | json | ndjson`
- `fields`: `string[]` or comma-separated string
- `max_diagnostics`: non-negative integer
- `dry_run`: boolean
- `unsafe_paths`: boolean

## Output Modes

### text

Human-readable diagnostics:

```text
trade.q:23:1: warning: possible cross join
trade.q:55:1: warning: unused variable 'tmp'
```

### json

Deterministic command envelope:

```json
{
  "command": "lint",
  "diagnostics": [
    {
      "column": 1,
      "file": "trade.q",
      "line": 23,
      "message": "possible cross join",
      "rule": "cross_join",
      "severity": "warning"
    }
  ],
  "dry_run": false,
  "errors": [],
  "exit_code": 1,
  "files": ["trade.q"],
  "files_scanned": 1,
  "ok": true,
  "output": "json",
  "summary": {
    "error": 0,
    "info": 0,
    "total": 1,
    "warning": 1
  }
}
```

### ndjson

Stream-friendly records (`diagnostic`, `error`, `summary`) for low-memory agent processing.

## Defensive Input Validation

By default, path arguments are validated to reduce dangerous/invalid agent-generated inputs.

- rejects control characters
- rejects `?`, `#`, `%` in paths (common hallucinated URL/resource fragments)

Use `--unsafe-paths` only when you intentionally need those characters.

## Current Rules

- `cross_join` (`warning`)
- `reserved_word` (`warning`)
- `unused_variable` (`warning`)
- `implicit_global` (`warning`)
- `nested_each` (`info`)
- `value_execution` (`info`)

## Exit Codes

- `0`: no issues
- `1`: warnings found (and no errors)
- `2`: errors found or command/input failures

## Environment Variable

- `QRINE_OUTPUT_FORMAT=text|json|ndjson`
- `QLINT_OUTPUT_FORMAT=text|json|ndjson` (legacy compatibility)

## Project Layout

```text
qrine/
  cli.py
  engine.py
  tokenizer.py
  parser.py
  diagnostics.py
  rules/
    __init__.py
    reserved_word.py
    cross_join.py
    unused_var.py
    implicit_global.py
    nested_each.py
    value_execution.py
qrine
README.md
philosophy.md
CONTEXT.md
```
