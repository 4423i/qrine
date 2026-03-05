from ..diagnostics import Diagnostic

# q null type identifiers that follow the number 0:
# 0N (long), 0n (float), 0Nd (date), 0Nt (time), 0Nu (minute), 0Nv (second),
# 0Nm (month), 0Np (timestamp), 0Nz (datetime), 0Nn (timespan), 0Ne (real)
NULL_TYPE_IDENTS = {"N", "n", "Nd", "Nt", "Nu", "Nv", "Nm", "Np", "Nz", "Nn", "Ne"}


class NullComparisonRule:
    name = "null_comparison"
    severity = "warning"

    def check(self, tokens, structure, text, file_path: str) -> list[Diagnostic]:
        diagnostics: list[Diagnostic] = []
        for i in range(len(tokens) - 2):
            t0, t1, t2 = tokens[i], tokens[i + 1], tokens[i + 2]
            if (
                t0.kind == "SYMBOL"
                and t0.value == "="
                and t1.kind == "NUMBER"
                and t1.value == "0"
                and t2.kind == "IDENT"
                and t2.value in NULL_TYPE_IDENTS
                and t0.line == t1.line == t2.line
            ):
                diagnostics.append(
                    Diagnostic(
                        file=file_path,
                        line=t0.line,
                        column=t0.column,
                        severity=self.severity,
                        rule=self.name,
                        message=f"use 'null' instead of '= 0{t2.value}'",
                    )
                )
        return diagnostics
