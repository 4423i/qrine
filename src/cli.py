import argparse
import json
import os
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .engine import compute_exit_code, lint_file

TARGET_EXTENSIONS = {".q", ".k"}
OUTPUT_FORMATS = {"text", "json", "ndjson"}
DIAGNOSTIC_FIELDS = ("file", "line", "column", "severity", "rule", "message")


@dataclass(frozen=True)
class CommandError:
    code: str
    message: str
    path: str | None = None

    def to_dict(self) -> dict[str, object]:
        payload: dict[str, object] = {"code": self.code, "message": self.message}
        if self.path is not None:
            payload["path"] = self.path
        return payload


@dataclass(frozen=True)
class LintConfig:
    paths: list[str]
    output: str
    fields: list[str] | None
    max_diagnostics: int | None
    dry_run: bool
    unsafe_paths: bool


def _reject_control_chars(value: str, label: str, allowed_controls: set[str] | None = None) -> None:
    allowed = allowed_controls or set()
    for char in value:
        if ord(char) < 0x20 and char not in allowed:
            raise ValueError(f"{label} contains control characters")


def _validate_path_arg(raw_path: str, unsafe_paths: bool) -> str:
    _reject_control_chars(raw_path, "path")
    if not unsafe_paths and any(ch in raw_path for ch in ("?", "#", "%")):
        raise ValueError("path contains forbidden characters (?, #, %) - use --unsafe-paths to bypass")
    return raw_path


def _parse_fields(raw_fields: str | list[str] | None) -> list[str] | None:
    if raw_fields is None:
        return None

    if isinstance(raw_fields, list):
        fields = [str(item).strip() for item in raw_fields if str(item).strip()]
    else:
        fields = [part.strip() for part in str(raw_fields).split(",") if part.strip()]

    if not fields:
        return None

    seen: set[str] = set()
    normalized: list[str] = []
    for field in fields:
        if field not in DIAGNOSTIC_FIELDS:
            allowed = ", ".join(DIAGNOSTIC_FIELDS)
            raise ValueError(f"invalid field '{field}' (allowed: {allowed})")
        if field not in seen:
            normalized.append(field)
            seen.add(field)

    return normalized


def _load_payload(raw_payload: str) -> dict[str, Any]:
    _reject_control_chars(raw_payload, "input JSON", allowed_controls={"\n", "\r", "\t"})
    try:
        payload = json.loads(raw_payload)
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid --input-json payload: {exc}") from exc

    if not isinstance(payload, dict):
        raise ValueError("--input-json payload must be a JSON object")

    allowed_keys = {"paths", "output", "fields", "max_diagnostics", "dry_run", "unsafe_paths"}
    unknown = sorted(set(payload.keys()) - allowed_keys)
    if unknown:
        raise ValueError(f"unknown keys in --input-json: {', '.join(unknown)}")

    return payload


def _resolve_output_format(explicit_output: str | None) -> str:
    output = explicit_output or os.getenv("QRINE_OUTPUT_FORMAT") or os.getenv("QLINT_OUTPUT_FORMAT", "text")
    if output not in OUTPUT_FORMATS:
        allowed = ", ".join(sorted(OUTPUT_FORMATS))
        raise ValueError(f"invalid output format '{output}' (allowed: {allowed})")
    return output


def _collect_files(paths: list[str], unsafe_paths: bool) -> tuple[list[Path], list[CommandError]]:
    errors: list[CommandError] = []
    unique: dict[Path, Path] = {}

    for raw in paths:
        try:
            safe_path = _validate_path_arg(raw, unsafe_paths=unsafe_paths)
        except ValueError as exc:
            errors.append(CommandError(code="invalid_path", message=str(exc), path=raw))
            continue

        path = Path(safe_path)
        if not path.exists():
            errors.append(CommandError(code="not_found", message="path does not exist", path=raw))
            continue

        if path.is_file():
            if path.suffix.lower() not in TARGET_EXTENSIONS:
                allowed = ", ".join(sorted(TARGET_EXTENSIONS))
                errors.append(
                    CommandError(
                        code="unsupported_extension",
                        message=f"file extension must be one of: {allowed}",
                        path=raw,
                    )
                )
                continue
            unique[path.resolve()] = path
            continue

        for sub in path.rglob("*"):
            if not sub.is_file() or sub.suffix.lower() not in TARGET_EXTENSIONS:
                continue
            unique[sub.resolve()] = sub

    files = sorted(unique.values(), key=lambda p: str(p))
    return files, errors


def _severity_summary(diagnostics) -> dict[str, int]:
    counter = Counter(d.severity for d in diagnostics)
    return {
        "error": int(counter.get("error", 0)),
        "warning": int(counter.get("warning", 0)),
        "info": int(counter.get("info", 0)),
        "total": len(diagnostics),
    }


def _project_diagnostic(diag, fields: list[str] | None) -> dict[str, object]:
    payload = diag.to_dict()
    if fields is None:
        return payload
    return {field: payload[field] for field in fields}


def _emit_json(payload: dict[str, object]) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))


def _emit_ndjson(
    diagnostics,
    errors: list[CommandError],
    summary: dict[str, int],
    fields: list[str] | None,
    dry_run: bool,
    files: list[Path],
    exit_code: int,
) -> None:
    if dry_run:
        for path in files:
            print(json.dumps({"type": "plan", "action": "lint", "file": str(path)}, sort_keys=True))

    for diag in diagnostics:
        event = {"type": "diagnostic", **_project_diagnostic(diag, fields)}
        print(json.dumps(event, sort_keys=True))

    for error in errors:
        print(json.dumps({"type": "error", **error.to_dict()}, sort_keys=True))

    print(
        json.dumps(
            {
                "type": "summary",
                "dry_run": dry_run,
                "exit_code": exit_code,
                "files_scanned": len(files),
                "summary": summary,
            },
            sort_keys=True,
        )
    )


def _merge_lint_config(args: argparse.Namespace, parser: argparse.ArgumentParser) -> LintConfig:
    try:
        payload = _load_payload(args.input_json) if args.input_json else {}
    except ValueError as exc:
        parser.error(str(exc))

    if args.json_output:
        args.output = "json"

    paths = args.paths or payload.get("paths", [])
    if not isinstance(paths, list) or not all(isinstance(item, str) for item in paths):
        parser.error("paths must be a list of strings")

    try:
        output = _resolve_output_format(args.output or payload.get("output"))
        fields = _parse_fields(args.fields if args.fields is not None else payload.get("fields"))
    except ValueError as exc:
        parser.error(str(exc))

    cli_max = args.max_diagnostics
    payload_max = payload.get("max_diagnostics")
    max_diagnostics = cli_max if cli_max is not None else payload_max
    if max_diagnostics is not None:
        if not isinstance(max_diagnostics, int) or max_diagnostics < 0:
            parser.error("max_diagnostics must be a non-negative integer")

    dry_run = bool(args.dry_run or payload.get("dry_run", False))
    unsafe_paths = bool(args.unsafe_paths or payload.get("unsafe_paths", False))

    return LintConfig(
        paths=paths,
        output=output,
        fields=fields,
        max_diagnostics=max_diagnostics,
        dry_run=dry_run,
        unsafe_paths=unsafe_paths,
    )


def _build_lint_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="qrine",
        description="kdb+/q static linter (agent-friendly deterministic output)",
    )
    parser.add_argument("paths", nargs="*", help="files or directories")
    parser.add_argument("--json", action="store_true", dest="json_output", help="alias of --output json")
    parser.add_argument("--output", choices=sorted(OUTPUT_FORMATS), help="output format")
    parser.add_argument("--input-json", help="raw JSON payload for lint options")
    parser.add_argument(
        "--fields",
        help="comma-separated diagnostic fields for json/ndjson (file,line,column,severity,rule,message)",
    )
    parser.add_argument("--max-diagnostics", type=int, help="maximum number of diagnostics to emit")
    parser.add_argument("--dry-run", action="store_true", help="validate inputs and show lint plan without reading files")
    parser.add_argument(
        "--unsafe-paths",
        action="store_true",
        help="allow path characters normally blocked for agent safety (?, #, %%)",
    )
    return parser


def _run_lint(argv: list[str]) -> int:
    parser = _build_lint_parser()
    args = parser.parse_args(argv)
    config = _merge_lint_config(args, parser)

    errors: list[CommandError] = []
    if not config.paths:
        errors.append(CommandError(code="no_paths", message="no input paths were provided"))

    files, path_errors = _collect_files(config.paths, unsafe_paths=config.unsafe_paths)
    errors.extend(path_errors)

    diagnostics = []
    if not config.dry_run:
        for path in files:
            try:
                diagnostics.extend(lint_file(path))
            except OSError as exc:
                errors.append(CommandError(code="read_failed", message=str(exc), path=str(path)))

    if config.max_diagnostics is not None:
        diagnostics = diagnostics[: config.max_diagnostics]

    summary = _severity_summary(diagnostics)
    exit_code = compute_exit_code(diagnostics)
    if errors:
        exit_code = 2

    if config.output == "text":
        if config.dry_run:
            for path in files:
                print(f"plan: lint {path}")
        for diag in diagnostics:
            print(diag.to_text())
        for error in errors:
            if error.path is not None:
                print(f"qrine: {error.code}: {error.path}: {error.message}", file=sys.stderr)
            else:
                print(f"qrine: {error.code}: {error.message}", file=sys.stderr)
    elif config.output == "json":
        _emit_json(
            {
                "command": "lint",
                "dry_run": config.dry_run,
                "errors": [item.to_dict() for item in errors],
                "exit_code": exit_code,
                "files": [str(path) for path in files],
                "files_scanned": len(files),
                "ok": not errors,
                "output": "json",
                "summary": summary,
                "diagnostics": [_project_diagnostic(diag, config.fields) for diag in diagnostics],
            }
        )
    else:
        _emit_ndjson(
            diagnostics=diagnostics,
            errors=errors,
            summary=summary,
            fields=config.fields,
            dry_run=config.dry_run,
            files=files,
            exit_code=exit_code,
        )

    return exit_code


def _schema_document() -> dict[str, object]:
    return {
        "tool": "qrine",
        "version": "1",
        "commands": {
            "lint": {
                "description": "Lint q/k source files",
                "input": {
                    "paths": ["string"],
                    "output": "text|json|ndjson",
                    "fields": list(DIAGNOSTIC_FIELDS),
                    "max_diagnostics": "integer >= 0",
                    "dry_run": "boolean",
                    "unsafe_paths": "boolean",
                },
                "output": {
                    "diagnostic": {
                        "file": "string",
                        "line": "integer",
                        "column": "integer",
                        "severity": "error|warning|info",
                        "rule": "string",
                        "message": "string",
                    },
                    "summary": {
                        "error": "integer",
                        "warning": "integer",
                        "info": "integer",
                        "total": "integer",
                    },
                    "exit_codes": {"0": "no issues", "1": "warnings", "2": "errors or command failures"},
                },
            },
            "schema": {
                "description": "Print runtime schema for agent introspection",
                "input": {"target": "all|lint.input|lint.output|diagnostic"},
                "output": "json",
            },
        },
    }


def _run_schema(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="qrine schema", description="runtime schema introspection")
    parser.add_argument("target", nargs="?", default="all", choices=["all", "lint.input", "lint.output", "diagnostic"])
    args = parser.parse_args(argv)

    doc = _schema_document()
    if args.target == "all":
        result: dict[str, object] = doc
    elif args.target == "lint.input":
        result = {"lint.input": doc["commands"]["lint"]["input"]}
    elif args.target == "lint.output":
        result = {"lint.output": doc["commands"]["lint"]["output"]}
    else:
        result = {"diagnostic": doc["commands"]["lint"]["output"]["diagnostic"]}

    _emit_json(result)
    return 0


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)

    if args and args[0] in {"schema", "describe"}:
        return _run_schema(args[1:])

    if args and args[0] == "lint":
        return _run_lint(args[1:])

    return _run_lint(args)


if __name__ == "__main__":
    raise SystemExit(main())
