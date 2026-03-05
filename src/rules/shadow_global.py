from ..diagnostics import Diagnostic

# q implicit default parameter names — shadowing these is expected and harmless
IMPLICIT_PARAMS = {"x", "y", "z"}


class ShadowGlobalRule:
    name = "shadow_global"
    severity = "info"

    def check(self, tokens, structure, text, file_path: str) -> list[Diagnostic]:
        diagnostics: list[Diagnostic] = []
        global_names: set[str] = set()
        for a in structure.get("assignments", []):
            global_names.add(str(a["name"]))
        for f in structure.get("functions", []):
            global_names.add(str(f["name"]))

        for fn in structure.get("functions", []):
            params = fn.get("params", [])
            if not params:
                continue
            fn_name = str(fn.get("name", ""))
            for param in params:
                if not param or param in IMPLICIT_PARAMS:
                    continue
                # param == fn_name means the function references itself — not a shadow
                if param != fn_name and param in global_names:
                    diagnostics.append(
                        Diagnostic(
                            file=file_path,
                            line=int(fn.get("line", 1)),
                            column=1,
                            severity=self.severity,
                            rule=self.name,
                            message=f"parameter '{param}' shadows global '{param}'",
                        )
                    )
        return diagnostics
