from pathlib import Path

from .diagnostics import Diagnostic
from .parser import parse_structure
from .rules import RULES
from .tokenizer import tokenize


def lint_text(text: str, file_path: str) -> list[Diagnostic]:
    tokens = tokenize(text)
    structure = parse_structure(tokens, text)

    diagnostics: list[Diagnostic] = []
    for rule in RULES:
        diagnostics.extend(rule.check(tokens=tokens, structure=structure, text=text, file_path=file_path))

    return sorted(diagnostics, key=lambda d: (d.line, d.column, d.severity, d.rule))


def lint_file(path: Path) -> list[Diagnostic]:
    text = path.read_text(encoding="utf-8")
    return lint_text(text, str(path))


def compute_exit_code(diagnostics: list[Diagnostic]) -> int:
    has_error = any(d.severity == "error" for d in diagnostics)
    if has_error:
        return 2
    has_warning = any(d.severity == "warning" for d in diagnostics)
    if has_warning:
        return 1
    return 0
