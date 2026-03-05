from dataclasses import dataclass

KEYWORDS = {
    "select",
    "update",
    "delete",
    "exec",
    "from",
    "where",
    "by",
}

MULTI_SYMBOLS = {"<>"}
SINGLE_SYMBOLS = set("+-*%=,;:(){}[]/")


@dataclass(frozen=True)
class Token:
    kind: str
    value: str
    line: int
    column: int


def _is_comment_start(text: str, index: int) -> bool:
    if text[index] != "/":
        return False
    cursor = index - 1
    while cursor >= 0 and text[cursor] != "\n":
        if not text[cursor].isspace():
            return False
        cursor -= 1
    return True


def tokenize(text: str) -> list[Token]:
    tokens: list[Token] = []
    i = 0
    line = 1
    column = 1

    while i < len(text):
        ch = text[i]

        if ch in " \t\r":
            i += 1
            column += 1
            continue

        if ch == "\n":
            i += 1
            line += 1
            column = 1
            continue

        if ch == "/" and _is_comment_start(text, i):
            while i < len(text) and text[i] != "\n":
                i += 1
                column += 1
            continue

        if i + 1 < len(text):
            pair = text[i : i + 2]
            if pair in MULTI_SYMBOLS:
                tokens.append(Token("SYMBOL", pair, line, column))
                i += 2
                column += 2
                continue

        if ch in SINGLE_SYMBOLS:
            tokens.append(Token("SYMBOL", ch, line, column))
            i += 1
            column += 1
            continue

        if ch == '"':
            start_col = column
            start = i
            i += 1
            column += 1
            while i < len(text):
                if text[i] == '"':
                    i += 1
                    column += 1
                    break
                if text[i] == "\n":
                    line += 1
                    column = 1
                    i += 1
                    continue
                i += 1
                column += 1
            tokens.append(Token("STRING", text[start:i], line, start_col))
            continue

        if ch == "`":
            start_col = column
            start = i
            i += 1
            column += 1
            while i < len(text) and (text[i].isalnum() or text[i] in "_."):
                i += 1
                column += 1
            tokens.append(Token("SYMBOL_LITERAL", text[start:i], line, start_col))
            continue

        if ch.isdigit():
            start = i
            start_col = column
            has_dot = False
            while i < len(text):
                if text[i].isdigit():
                    i += 1
                    column += 1
                    continue
                if text[i] == "." and not has_dot:
                    has_dot = True
                    i += 1
                    column += 1
                    continue
                break
            tokens.append(Token("NUMBER", text[start:i], line, start_col))
            continue

        if ch.isalpha() or ch == "_":
            start = i
            start_col = column
            while i < len(text) and (text[i].isalnum() or text[i] == "_"):
                i += 1
                column += 1
            value = text[start:i]
            lower = value.lower()
            if lower in KEYWORDS:
                tokens.append(Token(lower.upper(), value, line, start_col))
            else:
                tokens.append(Token("IDENT", value, line, start_col))
            continue

        tokens.append(Token("UNKNOWN", ch, line, column))
        i += 1
        column += 1

    return tokens
