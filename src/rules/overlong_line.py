from ..diagnostics import Diagnostic

MAX_LINE_LENGTH = 120


class OverlongLineRule:
    name = "overlong_line"
    severity = "info"

    def check(self, tokens, structure, text, file_path: str) -> list[Diagnostic]:
        diagnostics: list[Diagnostic] = []
        for i, line in enumerate(text.splitlines(), 1):
            if len(line) > MAX_LINE_LENGTH:
                diagnostics.append(
                    Diagnostic(
                        file=file_path,
                        line=i,
                        column=MAX_LINE_LENGTH + 1,
                        severity=self.severity,
                        rule=self.name,
                        message=f"line too long ({len(line)} > {MAX_LINE_LENGTH} characters)",
                    )
                )
        return diagnostics
