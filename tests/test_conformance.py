"""Conformance tests for Slice 1: strengthened MVP interpreter."""

from __future__ import annotations

import pytest

from setlhare.errors import SetlhareSyntaxError
from setlhare.runtime.interpreter import Interpreter


def run(src: str) -> Interpreter:
    i = Interpreter()
    i.run_source(src)
    return i


def out(capsys) -> str:
    return capsys.readouterr().out.strip()


# ── compound assignment ───────────────────────────────────────────────


def test_compound_add(capsys):
    run("mut x = 1\nx += 4\nprint(x)")
    assert out(capsys) == "5"


def test_compound_sub(capsys):
    run("mut x = 10\nx -= 3\nprint(x)")
    assert out(capsys) == "7"


def test_compound_mul(capsys):
    run("mut x = 3\nx *= 4\nprint(x)")
    assert out(capsys) == "12"


def test_compound_div(capsys):
    run("mut x = 10\nx /= 4\nprint(x)")
    assert out(capsys) == "2.5"


def test_compound_mod(capsys):
    run("mut x = 10\nx %= 3\nprint(x)")
    assert out(capsys) == "1"


def test_compound_string_concat(capsys):
    run('mut s = "hi"\ns += " there"\nprint(s)')
    assert out(capsys) == "hi there"


# ── index/attribute assignment ────────────────────────────────────────


def test_index_assign(capsys):
    run("mut xs = [1, 2, 3]\nxs[0] = 99\nprint(xs[0])")
    assert out(capsys) == "99"


def test_index_compound_assign(capsys):
    run("mut xs = [10, 20]\nxs[1] += 5\nprint(xs[1])")
    assert out(capsys) == "25"


def test_dict_index_assign(capsys):
    run('mut d = {"a": 1}\nd["a"] = 7\nprint(d["a"])')
    assert out(capsys) == "7"


def test_dict_new_key(capsys):
    run('mut d = {}\nd["k"] = "v"\nprint(d["k"])')
    assert out(capsys) == "v"


# ── string escapes ────────────────────────────────────────────────────


def test_newline_escape(capsys):
    run('print("a\\nb")')
    text = capsys.readouterr().out
    assert text == "a\nb\n"


def test_tab_escape(capsys):
    run('print("x\\ty")')
    assert capsys.readouterr().out == "x\ty\n"


def test_backslash_escape(capsys):
    run('print("c:\\\\path")')
    assert capsys.readouterr().out.rstrip("\n") == "c:\\path"


def test_quote_escape(capsys):
    run('print("she said \\"hi\\"")')
    assert capsys.readouterr().out.rstrip("\n") == 'she said "hi"'


def test_unknown_escape_rejected():
    with pytest.raises(SetlhareSyntaxError):
        Interpreter().run_source('print("\\q")')


# ── source-context error messages ─────────────────────────────────────


def test_syntax_error_contains_caret():
    with pytest.raises(SetlhareSyntaxError) as exc:
        Interpreter().run_source("func bad( {}")
    msg = str(exc.value)
    assert "^" in msg
    assert "-->" in msg


def test_syntax_error_contains_filename():
    with pytest.raises(SetlhareSyntaxError) as exc:
        Interpreter().run_source("func bad( {}", filename="demo.sl")
    assert "demo.sl" in str(exc.value)


# ── existing semantics still hold ─────────────────────────────────────


def test_for_loop_with_compound_accumulator(capsys):
    run("mut total = 0\nfor n in [1, 2, 3, 4] { total += n }\nprint(total)")
    assert out(capsys) == "10"


def test_string_interpolation_with_escapes(capsys):
    run('name := "Setlhare"\nprint("\\thi ${name}")')
    assert capsys.readouterr().out == "\thi Setlhare\n"
