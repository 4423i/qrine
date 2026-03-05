from ..diagnostics import Diagnostic


class SelectWithoutFromRule:
    name = "select_without_from"
    severity = "warning"

    def check(self, tokens, structure, text, file_path: str) -> list[Diagnostic]:
        diagnostics: list[Diagnostic] = []
        for stmt in structure.get("statements", []):
            if stmt.type not in ("SelectQuery", "ExecQuery"):
                continue
            if not stmt.data.get("from_raw"):
                query_type = str(stmt.data.get("type", stmt.type))
                diagnostics.append(
                    Diagnostic(
                        file=file_path,
                        line=stmt.line,
                        column=stmt.column,
                        severity=self.severity,
                        rule=self.name,
                        message=f"'{query_type}' without 'from' clause",
                    )
                )
        return diagnostics
