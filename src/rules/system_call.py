from ..diagnostics import Diagnostic


class SystemCallRule:
    name = "system_call"
    severity = "warning"

    def check(self, tokens, structure, text, file_path: str) -> list[Diagnostic]:
        diagnostics: list[Diagnostic] = []
        for token in tokens:
            if token.kind == "IDENT" and token.value == "system":
                diagnostics.append(
                    Diagnostic(
                        file=file_path,
                        line=token.line,
                        column=token.column,
                        severity=self.severity,
                        rule=self.name,
                        message="'system' call detected (side effects / audit concern)",
                    )
                )
        return diagnostics
