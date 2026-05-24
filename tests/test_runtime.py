from pathlib import Path
import pytest
from setlhare.runtime.interpreter import Interpreter
from setlhare.errors import ImmutableAssignmentError, SetlhareRuntimeError

ROOT = Path(__file__).resolve().parents[1]

def run(src: str):
    i = Interpreter(); i.run_source(src); return i

def test_function_and_interpolation(capsys):
    run('func square(n) => n * n\nname := "Setlhare"\nprint("Hello ${name} ${square(7)}")')
    assert capsys.readouterr().out.strip() == 'Hello Setlhare 49'

def test_immutable_assignment_rejected():
    with pytest.raises(ImmutableAssignmentError):
        run('x := 1\nx = 2')

def test_loops_and_list_pipeline(capsys):
    run('func square(n) => n * n\nfunc is_even(n) => n % 2 == 0\nxs := [1,2,3,4]\nprint(xs.filter(is_even).map(square).sum())')
    assert capsys.readouterr().out.strip() == '20'

def test_result_unwrap_error():
    with pytest.raises(SetlhareRuntimeError):
        run('x = Err("no")?')
