from ..diagnostics import Diagnostic


class DebugPrintRule:
    name = "debug_print"
    severity = "warning"

    def check(self, tokens, structure, text, file_path: str) -> list[Diagnostic]:
        diagnostics: list[Diagnostic] = []
        i = 0
        while i < len(tokens):
            token = tokens[i]
            # show x
            if token.kind == "IDENT" and token.value == "show":
                diagnostics.append(
                    Diagnostic(
                        file=file_path,
                        line=token.line,
                        column=token.column,
                        severity=self.severity,
                        rule=self.name,
                        message="debug output via 'show'",
                    )
                )
            # 0N! pattern: NUMBER "0", IDENT "N", UNKNOWN "!"
            if (
                token.kind == "NUMBER"
                and token.value == "0"
                and i + 2 < len(tokens)
                and tokens[i + 1].kind == "IDENT"
                and tokens[i + 1].value == "N"
                and tokens[i + 2].kind == "UNKNOWN"
                and tokens[i + 2].value == "!"
                and token.line == tokens[i + 1].line == tokens[i + 2].line
            ):
                diagnostics.append(
                    Diagnostic(
                        file=file_path,
                        line=token.line,
                        column=token.column,
                        severity=self.severity,
                        rule=self.name,
                        message="debug output via '0N!'",
                    )
                )
            i += 1
        return diagnostics
