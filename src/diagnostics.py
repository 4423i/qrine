from dataclasses import dataclass


@dataclass(frozen=True)
class Diagnostic:
    file: str
    line: int
    column: int
    severity: str
    rule: str
    message: str

    def to_dict(self) -> dict[str, object]:
        return {
            "file": self.file,
            "line": self.line,
            "column": self.column,
            "severity": self.severity,
            "rule": self.rule,
            "message": self.message,
        }

    def to_text(self) -> str:
        return f"{self.file}:{self.line}:{self.column}: {self.severity}: {self.message}"
