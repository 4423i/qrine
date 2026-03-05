from ..diagnostics import Diagnostic

_QUERY_KINDS = {"DELETE", "SELECT", "UPDATE", "EXEC"}


class DeleteWithoutWhereRule:
    name = "delete_without_where"
    severity = "warning"

    def check(self, tokens, structure, text, file_path: str) -> list[Diagnostic]:
        diagnostics: list[Diagnostic] = []
        i = 0
        while i < len(tokens):
            token = tokens[i]
            if token.kind != "DELETE":
                i += 1
                continue

            has_from = False
            has_where = False
            j = i + 1
            while j < len(tokens) and tokens[j].kind not in _QUERY_KINDS:
                if tokens[j].kind == "FROM":
                    has_from = True
                elif tokens[j].kind == "WHERE":
                    has_where = True
                j += 1

            if has_from and not has_where:
                diagnostics.append(
                    Diagnostic(
                        file=file_path,
                        line=token.line,
                        column=token.column,
                        severity=self.severity,
                        rule=self.name,
                        message="'delete from' without 'where' clause deletes all rows",
                    )
                )
            i = j
        return diagnostics
