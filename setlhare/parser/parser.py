from __future__ import annotations

from typing import Any
from setlhare.errors import SetlhareSyntaxError
from setlhare.lexer.lexer import Lexer
from setlhare.lexer.tokens import Token
from . import ast as A

class Parser:
    """Recursive-descent parser for the implemented Setlhare MVP grammar."""

    def parse(self, source: str) -> A.Module:
        self.tokens = Lexer().tokenize(source)
        self.current = 0
        body: list[Any] = []
        self._skip_separators()
        while not self._check("EOF"):
            body.append(self._declaration())
            self._skip_separators()
        first = self.tokens[0] if self.tokens else Token("EOF", "", 0, 0)
        return A.Module(first.line, first.col, body)

    def _declaration(self) -> Any:
        if self._match("IMPORT"): return self._import(self._previous())
        if self._match("FUNC"): return self._function(self._previous())
        return self._statement()

    def _statement(self) -> Any:
        if self._match("IF"): return self._if(self._previous())
        if self._match("WHILE"): return self._while(self._previous())
        if self._match("FOR"): return self._for(self._previous())
        if self._match("MATCH"): return self._match_stmt(self._previous())
        if self._match("RETURN"):
            tok = self._previous()
            value = None if self._is_separator() else self._expression()
            return A.Return(tok.line, tok.col, value)
        if self._match("BREAK"):
            tok = self._previous(); return A.Break(tok.line, tok.col)
        if self._match("CONTINUE"):
            tok = self._previous(); return A.Continue(tok.line, tok.col)
        if self._match("MUT"):
            tok = self._previous(); name = self._consume("ID", "expected binding name after 'mut'")
            typ = self._optional_type()
            self._consume("EQ", "expected '=' after mutable binding name")
            return A.Binding(tok.line, tok.col, name.value, self._expression(), True, typ)
        if self._check("ID") and self._peek_next().kind in {"COLON_EQ", "EQ", "COLON"}:
            name = self._advance()
            typ = self._optional_type()
            if self._match("COLON_EQ"):
                return A.Binding(name.line, name.col, name.value, self._expression(), False, typ)
            if self._match("EQ"):
                return A.Assign(name.line, name.col, name.value, self._expression())
            raise self._error(self._peek(), "expected ':=' or '=' after binding name/type")
        expr = self._expression()
        return A.ExprStmt(expr.line, expr.col, expr)

    def _import(self, tok: Token) -> A.Import:
        parts = [self._consume("ID", "expected module path after import").value]
        while self._match("DCOLON"):
            parts.append(self._consume("ID", "expected path component after '::'").value)
        return A.Import(tok.line, tok.col, "::".join(parts))

    def _function(self, tok: Token) -> A.Function:
        name = self._consume("ID", "expected function name")
        self._consume("LPAREN", "expected '(' after function name")
        params: list[str] = []
        if not self._check("RPAREN"):
            while True:
                p = self._consume("ID", "expected parameter name")
                self._optional_type()
                params.append(p.value)
                if not self._match("COMMA"): break
        self._consume("RPAREN", "expected ')' after parameters")
        ret = None
        if self._match("THIN_ARROW"):
            ret = self._consume("ID", "expected return type").value
        if self._match("ARROW"):
            expr = self._expression()
            return A.Function(tok.line, tok.col, name.value, params, A.Block(tok.line, tok.col, [A.Return(expr.line, expr.col, expr)]), ret)
        body = self._block()
        return A.Function(tok.line, tok.col, name.value, params, body, ret)

    def _if(self, tok: Token) -> A.If:
        cond = self._expression(); then = self._block(); elifs = []
        while True:
            self._skip_separators()
            if not self._match("ELIF"): break
            c = self._expression(); b = self._block(); elifs.append((c, b))
        else_block = None
        self._skip_separators()
        if self._match("ELSE"):
            else_block = self._block()
        return A.If(tok.line, tok.col, cond, then, elifs, else_block)

    def _while(self, tok: Token) -> A.While:
        return A.While(tok.line, tok.col, self._expression(), self._block())

    def _for(self, tok: Token) -> A.For:
        name = self._consume("ID", "expected loop variable")
        self._consume("IN", "expected 'in' after loop variable")
        iterable = self._expression()
        return A.For(tok.line, tok.col, name.value, iterable, self._block())

    def _match_stmt(self, tok: Token) -> A.Match:
        value = self._expression(); self._consume("LBRACE", "expected '{' after match expression")
        cases: list[A.MatchCase] = []
        self._skip_separators()
        while not self._check("RBRACE") and not self._check("EOF"):
            wildcard = False
            if self._match("CASE"):
                pattern = self._expression()
            elif self._match("ID") and self._previous().value == "_":
                pattern = None; wildcard = True
            else:
                raise self._error(self._peek(), "expected 'case' or '_' in match")
            self._consume("ARROW", "expected '=>' in match case")
            if self._match("LBRACE"):
                body = self._block_after_open()
            else:
                expr = self._expression()
                body = A.Block(expr.line, expr.col, [A.Return(expr.line, expr.col, expr)])
            cases.append(A.MatchCase(tok.line, tok.col, pattern, body, wildcard))
            self._skip_separators()
        self._consume("RBRACE", "expected '}' after match")
        return A.Match(tok.line, tok.col, value, cases)

    def _block(self) -> A.Block:
        self._consume("LBRACE", "expected '{' to start block")
        return self._block_after_open()

    def _block_after_open(self) -> A.Block:
        body = []
        self._skip_separators()
        while not self._check("RBRACE") and not self._check("EOF"):
            body.append(self._declaration())
            self._skip_separators()
        end = self._consume("RBRACE", "expected '}' after block")
        return A.Block(end.line, end.col, body)

    def _expression(self) -> Any:
        return self._or()

    def _or(self):
        expr = self._and()
        while self._match("OR", "OROR"):
            op = self._previous(); expr = A.Binary(op.line, op.col, expr, "or", self._and())
        return expr

    def _and(self):
        expr = self._equality()
        while self._match("AND", "ANDAND"):
            op = self._previous(); expr = A.Binary(op.line, op.col, expr, "and", self._equality())
        return expr

    def _equality(self):
        expr = self._comparison()
        while self._match("EQEQ", "BANGEQ"):
            op = self._previous(); expr = A.Binary(op.line, op.col, expr, op.value, self._comparison())
        return expr

    def _comparison(self):
        expr = self._term()
        while self._match("LT", "LTE", "GT", "GTE"):
            op = self._previous(); expr = A.Binary(op.line, op.col, expr, op.value, self._term())
        return expr

    def _term(self):
        expr = self._factor()
        while self._match("PLUS", "MINUS"):
            op = self._previous(); expr = A.Binary(op.line, op.col, expr, op.value, self._factor())
        return expr

    def _factor(self):
        expr = self._unary()
        while self._match("STAR", "SLASH", "PERCENT"):
            op = self._previous(); expr = A.Binary(op.line, op.col, expr, op.value, self._unary())
        return expr

    def _unary(self):
        if self._match("BANG", "MINUS", "NOT"):
            op = self._previous(); return A.Unary(op.line, op.col, op.value, self._unary())
        if self._match("SPAWN", "GO"):
            tok = self._previous(); call = self._postfix()
            if not isinstance(call, A.Call):
                raise self._error(tok, f"{tok.value} expects a function call")
            return A.Spawn(tok.line, tok.col, call, tok.value)
        return self._postfix()

    def _postfix(self):
        expr = self._primary()
        while True:
            if self._match("LPAREN"):
                args = []
                if not self._check("RPAREN"):
                    while True:
                        args.append(self._expression())
                        if not self._match("COMMA"): break
                paren = self._consume("RPAREN", "expected ')' after arguments")
                expr = A.Call(paren.line, paren.col, expr, args)
            elif self._match("DOT"):
                name = self._consume("ID", "expected property name after '.'")
                expr = A.GetAttr(name.line, name.col, expr, name.value)
            elif self._match("LBRACKET"):
                idx = self._expression(); rb = self._consume("RBRACKET", "expected ']' after index")
                expr = A.Index(rb.line, rb.col, expr, idx)
            elif self._match("QUESTION"):
                q = self._previous(); expr = A.ResultUnwrap(q.line, q.col, expr)
            else:
                break
        return expr

    def _primary(self):
        if self._match("INT"):
            t = self._previous(); return A.Literal(t.line, t.col, int(t.value), t.value)
        if self._match("FLOAT"):
            t = self._previous(); return A.Literal(t.line, t.col, float(t.value), t.value)
        if self._match("STRING"):
            t = self._previous(); return A.Literal(t.line, t.col, t.value[1:-1], t.value)
        if self._match("TRUE"):
            t = self._previous(); return A.Literal(t.line, t.col, True, t.value)
        if self._match("FALSE"):
            t = self._previous(); return A.Literal(t.line, t.col, False, t.value)
        if self._match("NIL"):
            t = self._previous(); return A.Literal(t.line, t.col, None, t.value)
        if self._match("ID"):
            t = self._previous(); return A.Name(t.line, t.col, t.value)
        if self._match("LPAREN"):
            expr = self._expression(); self._consume("RPAREN", "expected ')' after expression"); return expr
        if self._match("LBRACKET"):
            items = []
            if not self._check("RBRACKET"):
                while True:
                    items.append(self._expression())
                    if not self._match("COMMA"): break
            rb = self._consume("RBRACKET", "expected ']' after list")
            return A.ListExpr(rb.line, rb.col, items)
        if self._match("LBRACE"):
            if self._match("RBRACE"):
                t = self._previous(); return A.DictExpr(t.line, t.col, [])
            first = self._expression()
            if self._match("COLON"):
                items = [(first, self._expression())]
                while self._match("COMMA"):
                    if self._check("RBRACE"): break
                    k = self._expression(); self._consume("COLON", "expected ':' in dict literal"); items.append((k, self._expression()))
                rb = self._consume("RBRACE", "expected '}' after dict")
                return A.DictExpr(rb.line, rb.col, items)
            items = [first]
            while self._match("COMMA"):
                if self._check("RBRACE"): break
                items.append(self._expression())
            rb = self._consume("RBRACE", "expected '}' after set")
            return A.SetExpr(rb.line, rb.col, items)
        raise self._error(self._peek(), "expected expression")

    def _optional_type(self) -> str | None:
        if self._match("COLON"):
            return self._consume("ID", "expected type name after ':'").value
        return None

    def _skip_separators(self) -> None:
        while self._match("NEWLINE", "SEMI"):
            pass

    def _is_separator(self) -> bool:
        return self._check("NEWLINE") or self._check("SEMI") or self._check("RBRACE") or self._check("EOF")

    def _match(self, *kinds: str) -> bool:
        if self._check(*kinds):
            self._advance(); return True
        return False

    def _consume(self, kind: str, msg: str) -> Token:
        if self._check(kind): return self._advance()
        raise self._error(self._peek(), msg)

    def _check(self, *kinds: str) -> bool:
        return self._peek().kind in kinds

    def _advance(self) -> Token:
        if not self._check("EOF"): self.current += 1
        return self._previous()

    def _peek(self) -> Token:
        return self.tokens[self.current]

    def _peek_next(self) -> Token:
        return self.tokens[min(self.current + 1, len(self.tokens) - 1)]

    def _previous(self) -> Token:
        return self.tokens[self.current - 1]

    def _error(self, tok: Token, msg: str) -> SetlhareSyntaxError:
        return SetlhareSyntaxError(f"{msg} at {tok.line}:{tok.col}; saw {tok.kind} {tok.value!r}")
