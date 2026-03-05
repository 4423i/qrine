import re
from dataclasses import dataclass, field

from .tokenizer import KEYWORDS, Token

ASSIGN_RE = re.compile(r"^(\.[A-Za-z_][A-Za-z0-9_.]*|[A-Za-z_][A-Za-z0-9_]*)\s*:\s*(.*)$")
QUERY_RE = re.compile(r"^(select|exec|update|delete)\b", re.IGNORECASE)
FROM_RE = re.compile(r"\bfrom\b\s+(.+?)(?=\bwhere\b|\bby\b|$)", re.IGNORECASE)
IDENT_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
NS_DIRECTIVE_RE = re.compile(r"^\\d\s+(\S+)")


@dataclass(frozen=True)
class Statement:
    type: str
    line: int
    column: int
    data: dict[str, object] = field(default_factory=dict)


def _strip_comment(line: str) -> str:
    if line.lstrip().startswith("/"):
        return ""
    return line


def _count_braces(s: str) -> int:
    """Net open-brace count, skipping content inside double-quoted strings."""
    depth = 0
    in_str = False
    for ch in s:
        if in_str:
            if ch == '"':
                in_str = False
        else:
            if ch == '"':
                in_str = True
            elif ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
    return depth


def _logical_lines(text: str) -> list[tuple[int, str]]:
    """Join continuation lines into brace-balanced logical lines.

    Returns list of (start_line_number, joined_content).
    Handles multi-line function definitions like:
        f:{[x;y]
          z:x+y;
          z*2}
    """
    result = []
    parts: list[str] = []
    start: int | None = None
    depth = 0

    in_block = False
    for lineno, raw_line in enumerate(text.splitlines(), start=1):
        stripped_raw = raw_line.strip()
        if not in_block:
            if stripped_raw == "/":
                in_block = True
                continue
        else:
            if stripped_raw == "\\":
                in_block = False
            continue
        line = _strip_comment(raw_line).strip()
        if not line:
            continue
        if start is None:
            start = lineno
        parts.append(line)
        depth += _count_braces(line)
        if depth <= 0:
            result.append((start, " ".join(parts)))
            parts = []
            start = None
            depth = 0

    if parts and start is not None:
        result.append((start, " ".join(parts)))

    return result


def _parse_function_body(rhs: str) -> tuple[list[str], str] | None:
    rhs = rhs.strip()
    if not (rhs.startswith("{") and rhs.endswith("}")):
        return None

    body = rhs[1:-1].strip()
    params: list[str] = []
    if body.startswith("["):
        close = body.find("]")
        if close != -1:
            param_text = body[1:close].strip()
            body = body[close + 1 :].strip()
            if param_text:
                params = [p.strip() for p in param_text.split(";") if p.strip()]
    return params, body


def _parse_from_tables(source: str) -> list[str]:
    tables: list[str] = []
    for raw in source.split(","):
        token = raw.strip().split()
        if not token:
            continue
        name = token[0].strip("`")
        if name:
            tables.append(name)
    return tables


def parse_structure(tokens: list[Token], text: str) -> dict[str, object]:
    statements: list[Statement] = []
    assignments: list[dict[str, object]] = []
    functions: list[dict[str, object]] = []
    current_ns = ""

    for lineno, line in _logical_lines(text):
        # \d namespace directive
        ns_match = NS_DIRECTIVE_RE.match(line)
        if ns_match:
            ns = ns_match.group(1)
            current_ns = "" if ns == "." else ns
            continue

        assign_match = ASSIGN_RE.match(line)
        if assign_match:
            name = assign_match.group(1)
            rhs = assign_match.group(2)
            namespace = current_ns if (current_ns and not name.startswith(".")) else ""
            fn_info = _parse_function_body(rhs)
            if fn_info is not None:
                params, body = fn_info
                entry = {"name": name, "namespace": namespace, "params": params, "body": body, "line": lineno}
                functions.append(entry)
                statements.append(Statement("FunctionDef", lineno, 1, entry))
            else:
                entry = {"name": name, "namespace": namespace, "line": lineno}
                assignments.append(entry)
                statements.append(Statement("Assignment", lineno, 1, entry))
            continue

        query_match = QUERY_RE.match(line)
        if query_match:
            query = query_match.group(1).lower()
            from_match = FROM_RE.search(line)
            from_raw = from_match.group(1).strip() if from_match else ""
            from_tables = _parse_from_tables(from_raw) if from_raw else []
            qentry = {"type": query, "line": lineno, "from_raw": from_raw, "from_tables": from_tables}
            if query == "select":
                stype = "SelectQuery"
            elif query == "exec":
                stype = "ExecQuery"
            elif query == "update":
                stype = "UpdateQuery"
            else:
                stype = "DeleteQuery"
            statements.append(Statement(stype, lineno, 1, qentry))
            continue

        statements.append(Statement("Expression", lineno, 1, {"text": line}))

    return {
        "statements": statements,
        "assignments": assignments,
        "functions": functions,
        "identifiers": [t for t in tokens if t.kind == "IDENT" and t.value.lower() not in KEYWORDS],
    }
