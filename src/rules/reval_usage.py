from ..diagnostics import Diagnostic


class RevalUsageRule:
    name = "reval_usage"
    severity = "info"

    def check(self, tokens, structure, text, file_path: str) -> list[Diagnostic]:
        diagnostics: list[Diagnostic] = []
        for token in tokens:
            if token.kind == "IDENT" and token.value == "reval":
                diagnostics.append(
                    Diagnostic(
                        file=file_path,
                        line=token.line,
                        column=token.column,
                        severity=self.severity,
                        rule=self.name,
                        message="dynamic evaluation via 'reval'",
                    )
                )
        return diagnostics
