from ..diagnostics import Diagnostic


class HopenNotClosedRule:
    name = "hopen_not_closed"
    severity = "info"

    def check(self, tokens, structure, text, file_path: str) -> list[Diagnostic]:
        diagnostics: list[Diagnostic] = []

        # Collect lines that have an assignment (IDENT followed by ":" on the same line).
        # hopen on such a line is assumed to be the assigned value.
        assigned_lines: set[int] = set()
        for i, token in enumerate(tokens[:-1]):
            nxt = tokens[i + 1]
            if token.kind == "IDENT" and nxt.kind == "SYMBOL" and nxt.value == ":" and token.line == nxt.line:
                assigned_lines.add(token.line)

        for token in tokens:
            if token.kind == "IDENT" and token.value == "hopen":
                if token.line not in assigned_lines:
                    diagnostics.append(
                        Diagnostic(
                            file=file_path,
                            line=token.line,
                            column=token.column,
                            severity=self.severity,
                            rule=self.name,
                            message="'hopen' return value not assigned (possible handle leak)",
                        )
                    )
        return diagnostics
