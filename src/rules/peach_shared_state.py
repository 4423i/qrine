import re

from ..diagnostics import Diagnostic

PEACH_RE = re.compile(r"\bpeach\b")
GLOBAL_AMEND_RE = re.compile(r"::")


class PeachSharedStateRule:
    name = "peach_shared_state"
    severity = "warning"

    def check(self, tokens, structure, text, file_path: str) -> list[Diagnostic]:
        diagnostics: list[Diagnostic] = []
        for fn in structure.get("functions", []):
            body = str(fn.get("body", ""))
            if PEACH_RE.search(body) and GLOBAL_AMEND_RE.search(body):
                name = fn.get("name", "?")
                diagnostics.append(
                    Diagnostic(
                        file=file_path,
                        line=int(fn.get("line", 1)),
                        column=1,
                        severity=self.severity,
                        rule=self.name,
                        message=f"'peach' used with global state mutation ('::') in function '{name}'",
                    )
                )
        return diagnostics
