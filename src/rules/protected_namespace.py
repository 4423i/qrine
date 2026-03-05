from ..diagnostics import Diagnostic

# .q namespace contains q built-in functions; overriding them silently breaks code
_PROTECTED_PREFIX = ".q."


class ProtectedNamespaceRule:
    name = "protected_namespace"
    severity = "warning"

    def check(self, tokens, structure, text, file_path: str) -> list[Diagnostic]:
        diagnostics: list[Diagnostic] = []
        for stmt in structure.get("statements", []):
            if stmt.type not in ("Assignment", "FunctionDef"):
                continue
            name = str(stmt.data.get("name", ""))
            namespace = str(stmt.data.get("namespace", ""))

            # Build fully qualified name
            if name.startswith("."):
                fqn = name
            elif namespace:
                fqn = f"{namespace}.{name}"
            else:
                fqn = name

            if fqn.startswith(_PROTECTED_PREFIX):
                diagnostics.append(
                    Diagnostic(
                        file=file_path,
                        line=stmt.line,
                        column=stmt.column,
                        severity=self.severity,
                        rule=self.name,
                        message=f"assignment to '{fqn}' overrides a q built-in function",
                    )
                )
        return diagnostics
