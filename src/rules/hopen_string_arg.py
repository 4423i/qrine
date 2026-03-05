from ..diagnostics import Diagnostic


class HopenStringArgRule:
    name = "hopen_string_arg"
    severity = "info"

    def check(self, tokens, structure, text, file_path: str) -> list[Diagnostic]:
        diagnostics: list[Diagnostic] = []
        for i, token in enumerate(tokens[:-1]):
            if token.kind != "IDENT" or token.value != "hopen":
                continue
            nxt = tokens[i + 1]
            if nxt.kind == "STRING" and token.line == nxt.line:
                diagnostics.append(
                    Diagnostic(
                        file=file_path,
                        line=token.line,
                        column=token.column,
                        severity=self.severity,
                        rule=self.name,
                        message="'hopen' with string argument; prefer symbol (`:host:port)",
                    )
                )
        return diagnostics
