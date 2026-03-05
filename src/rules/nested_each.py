from ..diagnostics import Diagnostic


class NestedEachRule:
    name = "nested_each"
    severity = "info"

    def check(self, tokens, structure, text, file_path: str) -> list[Diagnostic]:
        diagnostics: list[Diagnostic] = []
        lines: dict[int, int] = {}
        for token in tokens:
            if token.kind == "IDENT" and token.value.lower() == "each":
                lines[token.line] = lines.get(token.line, 0) + 1

        for line, count in lines.items():
            if count >= 2:
                diagnostics.append(
                    Diagnostic(
                        file=file_path,
                        line=line,
                        column=1,
                        severity=self.severity,
                        rule=self.name,
                        message="nested each detected",
                    )
                )
        return diagnostics
