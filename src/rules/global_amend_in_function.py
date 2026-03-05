import re

from ..diagnostics import Diagnostic

# Matches IDENT:: — global variable amend syntax inside a function body
GLOBAL_AMEND_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*\s*::")


class GlobalAmendInFunctionRule:
    name = "global_amend_in_function"
    severity = "warning"

    def check(self, tokens, structure, text, file_path: str) -> list[Diagnostic]:
        diagnostics: list[Diagnostic] = []
        for fn in structure.get("functions", []):
            body = str(fn.get("body", ""))
            if GLOBAL_AMEND_RE.search(body):
                name = fn.get("name", "?")
                diagnostics.append(
                    Diagnostic(
                        file=file_path,
                        line=int(fn.get("line", 1)),
                        column=1,
                        severity=self.severity,
                        rule=self.name,
                        message=f"global variable mutated via '::' in function '{name}'",
                    )
                )
        return diagnostics
