from __future__ import annotations

from setlhare.errors import SetlhareSyntaxError
from .tokens import KEYWORDS, Token

SINGLE = {
    "(": "LPAREN", ")": "RPAREN", "{": "LBRACE", "}": "RBRACE",
    "[": "LBRACKET", "]": "RBRACKET", ",": "COMMA", ".": "DOT",
    ":": "COLON", ";": "SEMI", "@": "AT", "#": "HASH", "?": "QUESTION",
    "+": "PLUS", "-": "MINUS", "*": "STAR", "/": "SLASH", "%": "PERCENT",
    "<": "LT", ">": "GT", "=": "EQ", "!": "BANG", "|": "PIPE", "&": "AMP",
}
DOUBLE = {
    "=>": "ARROW", ":=": "COLON_EQ", "::": "DCOLON", "==": "EQEQ", "!=": "BANGEQ",
    "<=": "LTE", ">=": "GTE", "&&": "ANDAND", "||": "OROR", "->": "THIN_ARROW",
}

class Lexer:
    """Unicode-aware, deterministic Setlhare lexer with precise diagnostics."""

    def tokenize(self, source: str) -> list[Token]:
        tokens: list[Token] = []
        i = 0
        line = 1
        col = 1
        n = len(source)
        while i < n:
            ch = source[i]
            if ch in " \t\r":
                i += 1; col += 1; continue
            if ch == "\n":
                tokens.append(Token("NEWLINE", ch, line, col))
                i += 1; line += 1; col = 1; continue
            if source.startswith("//", i):
                while i < n and source[i] != "\n":
                    i += 1; col += 1
                continue
            if source.startswith("/*", i):
                start_line, start_col = line, col
                i += 2; col += 2
                while i < n and not source.startswith("*/", i):
                    if source[i] == "\n":
                        line += 1; col = 1; i += 1
                    else:
                        i += 1; col += 1
                if i >= n:
                    raise SetlhareSyntaxError(f"unterminated block comment at {start_line}:{start_col}")
                i += 2; col += 2; continue
            if ch == '"':
                start_i, start_line, start_col = i, line, col
                i += 1; col += 1; escaped = False
                while i < n:
                    c = source[i]
                    if escaped:
                        escaped = False; i += 1; col += 1; continue
                    if c == "\\":
                        escaped = True; i += 1; col += 1; continue
                    if c == '"':
                        i += 1; col += 1
                        tokens.append(Token("STRING", source[start_i:i], start_line, start_col))
                        break
                    if c == "\n":
                        raise SetlhareSyntaxError(f"unterminated string at {start_line}:{start_col}")
                    i += 1; col += 1
                else:
                    raise SetlhareSyntaxError(f"unterminated string at {start_line}:{start_col}")
                continue
            if ch.isdigit():
                start_i, start_col = i, col
                while i < n and source[i].isdigit():
                    i += 1; col += 1
                if i < n and source[i] == "." and i + 1 < n and source[i+1].isdigit():
                    i += 1; col += 1
                    while i < n and source[i].isdigit():
                        i += 1; col += 1
                    kind = "FLOAT"
                else:
                    kind = "INT"
                tokens.append(Token(kind, source[start_i:i], line, start_col)); continue
            if ch.isalpha() or ch == "_":
                start_i, start_col = i, col
                while i < n and (source[i].isalnum() or source[i] == "_"):
                    i += 1; col += 1
                value = source[start_i:i]
                kind = value.upper() if value in KEYWORDS else "ID"
                tokens.append(Token(kind, value, line, start_col)); continue
            two = source[i:i+2]
            if two in DOUBLE:
                tokens.append(Token(DOUBLE[two], two, line, col)); i += 2; col += 2; continue
            if ch in SINGLE:
                tokens.append(Token(SINGLE[ch], ch, line, col)); i += 1; col += 1; continue
            raise SetlhareSyntaxError(f"unexpected character {ch!r} at {line}:{col}")
        tokens.append(Token("EOF", "", line, col))
        return tokens
