import re

from ..diagnostics import Diagnostic

EXIT_RE = re.compile(r"\bexit\b")


class ExitInFunctionRule:
    name = "exit_in_function"
    severity = "error"

    def check(self, tokens, structure, text, file_path: str) -> list[Diagnostic]:
        diagnostics: list[Diagnostic] = []
        for fn in structure.get("functions", []):
            body = str(fn.get("body", ""))
            if EXIT_RE.search(body):
                name = fn.get("name", "?")
                diagnostics.append(
                    Diagnostic(
                        file=file_path,
                        line=int(fn.get("line", 1)),
                        column=1,
                        severity=self.severity,
                        rule=self.name,
                        message=f"'exit' inside function '{name}' terminates the process",
                    )
                )
        return diagnostics
