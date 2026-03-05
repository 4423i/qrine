import re
from collections import Counter

from ..diagnostics import Diagnostic


def _is_ns_name(name: str) -> bool:
    return name.startswith(".")


def _ns_name_used(name: str, text: str) -> bool:
    # Namespace-qualified names (e.g. .myns.val) are not single IDENT tokens,
    # so token-based counting fails. Fall back to raw text search.
    # The name appears at least once (its own definition), so >1 means it's used.
    pattern = re.compile(re.escape(name) + r"(?![A-Za-z0-9_.])")
    return len(pattern.findall(text)) > 1


class UnusedVarRule:
    name = "unused_variable"
    severity = "warning"

    def check(self, tokens, structure, text, file_path: str) -> list[Diagnostic]:
        assignments = structure.get("assignments", [])
        if not assignments:
            return []

        assignment_positions: set[tuple[int, int, str]] = set()
        for i, token in enumerate(tokens[:-1]):
            nxt = tokens[i + 1]
            if token.kind != "IDENT":
                continue
            if nxt.kind == "SYMBOL" and nxt.value == ":" and token.line == nxt.line:
                assignment_positions.add((token.line, token.column, token.value))

        usage = Counter()
        for token in tokens:
            if token.kind != "IDENT":
                continue
            marker = (token.line, token.column, token.value)
            if marker in assignment_positions:
                continue
            usage[token.value] += 1

        diagnostics: list[Diagnostic] = []
        for entry in assignments:
            name = str(entry["name"])
            line = int(entry["line"])
            if _is_ns_name(name):
                used = _ns_name_used(name, text)
            else:
                used = usage.get(name, 0) > 0
            if not used:
                diagnostics.append(
                    Diagnostic(
                        file=file_path,
                        line=line,
                        column=1,
                        severity=self.severity,
                        rule=self.name,
                        message=f"unused variable '{name}'",
                    )
                )
        return diagnostics
