from ..diagnostics import Diagnostic

MAX_PARAMS = 5


class FunctionManyParamsRule:
    name = "function_many_params"
    severity = "info"

    def check(self, tokens, structure, text, file_path: str) -> list[Diagnostic]:
        diagnostics: list[Diagnostic] = []
        for fn in structure.get("functions", []):
            params = fn.get("params", [])
            if len(params) > MAX_PARAMS:
                name = fn.get("name", "?")
                diagnostics.append(
                    Diagnostic(
                        file=file_path,
                        line=int(fn.get("line", 1)),
                        column=1,
                        severity=self.severity,
                        rule=self.name,
                        message=f"function '{name}' has {len(params)} parameters (>{MAX_PARAMS}); consider a dictionary argument",
                    )
                )
        return diagnostics
