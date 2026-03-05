import re

from ..diagnostics import Diagnostic

IDENT_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
LOCAL_ASSIGN_RE = re.compile(r"\b([A-Za-z_][A-Za-z0-9_]*)\s*:")
EXCLUDE = {"select", "update", "delete", "exec", "from", "where", "by", "each", "value"}


class ImplicitGlobalRule:
    name = "implicit_global"
    severity = "warning"

    def check(self, tokens, structure, text, file_path: str) -> list[Diagnostic]:
        diagnostics: list[Diagnostic] = []
        for fn in structure.get("functions", []):
            params = [p for p in fn.get("params", []) if p]
            allowed = set(params) if params else {"x", "y"}
            body = str(fn.get("body", ""))

            local_names = set(LOCAL_ASSIGN_RE.findall(body))
            idents = {name for name in IDENT_RE.findall(body) if name.lower() not in EXCLUDE}
            globals_used = sorted(name for name in idents if name not in allowed and name not in local_names)

            for name in globals_used:
                diagnostics.append(
                    Diagnostic(
                        file=file_path,
                        line=int(fn.get("line", 1)),
                        column=1,
                        severity=self.severity,
                        rule=self.name,
                        message=f"implicit global variable '{name}'",
                    )
                )
        return diagnostics
