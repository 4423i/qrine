from ..diagnostics import Diagnostic


class ValueExecutionRule:
    name = "value_execution"
    severity = "info"

    def check(self, tokens, structure, text, file_path: str) -> list[Diagnostic]:
        diagnostics: list[Diagnostic] = []
        for i, token in enumerate(tokens):
            if token.kind != "IDENT" or token.value.lower() != "value":
                continue
            if i + 1 < len(tokens) and tokens[i + 1].kind == "STRING":
                diagnostics.append(
                    Diagnostic(
                        file=file_path,
                        line=token.line,
                        column=token.column,
                        severity=self.severity,
                        rule=self.name,
                        message="dynamic evaluation via value",
                    )
                )
        return diagnostics
