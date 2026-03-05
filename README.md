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

### Error
- `exit_in_function` — `exit` inside a function terminates the whole process

### Warning
- `cross_join` — possible cross join (multiple tables without join condition)
- `reserved_word` — variable/parameter name conflicts with q built-in
- `unused_variable` — assigned variable never read
- `implicit_global` — function references global variable without explicit assignment
- `null_comparison` — `= 0N` / `= 0n` etc. should be `null x`
- `global_amend_in_function` — global mutation via `::` inside a function
- `delete_without_where` — `delete from table` without `where` deletes all rows
- `update_without_where` — `update from table` without `where` modifies all rows
- `protected_namespace` — assignment to `.q.*` overrides a q built-in function
- `peach_shared_state` — `peach` combined with global mutation `::` (race condition)
- `debug_print` — `show` or `0N!` debug output left in code
- `system_call` — `system` call (side effects / audit concern)

### Info
- `nested_each` — nested `each` (potential performance concern)
- `value_execution` — dynamic evaluation via `value`
- `reval_usage` — dynamic evaluation via `reval`
- `hopen_not_closed` — `hopen` return value not assigned (possible handle leak)
- `hopen_string_arg` — `hopen` with string argument; prefer symbol (`:host:port)
- `shadow_global` — function parameter shadows a global name
- `overlong_line` — line exceeds 120 characters
- `function_many_params` — function has more than 5 parameters
- `select_without_from` — `select`/`exec` without `from` clause

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
