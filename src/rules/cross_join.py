from ..diagnostics import Diagnostic


class CrossJoinRule:
    name = "cross_join"
    severity = "warning"

    def check(self, tokens, structure, text, file_path: str) -> list[Diagnostic]:
        diagnostics: list[Diagnostic] = []
        for stmt in structure.get("statements", []):
            if stmt.type != "SelectQuery":
                continue
            from_raw = str(stmt.data.get("from_raw", ""))
            from_tables = stmt.data.get("from_tables", [])
            if "," in from_raw and len(from_tables) >= 2:
                diagnostics.append(
                    Diagnostic(
                        file=file_path,
                        line=stmt.line,
                        column=stmt.column,
                        severity=self.severity,
                        rule=self.name,
                        message="possible cross join",
                    )
                )
        return diagnostics
