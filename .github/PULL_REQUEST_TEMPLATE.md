## Summary

<!-- One paragraph. What does this PR do, and why? -->

## Spec impact

- [ ] No observable language behavior changes
- [ ] Spec updated (link the file(s) below)

Spec files touched: `docs/spec/...`

## Tests

- [ ] New unit tests added
- [ ] Regression test for the bug being fixed (if applicable)
- [ ] Conformance test added under `tests/conformance/` (if a language feature)

## Checklist

- [ ] `ruff check . && ruff format --check .` passes
- [ ] `mypy setlhare` passes
- [ ] `pytest -q` passes
- [ ] Examples still run: `for f in examples/*.sl; do setlhare check "$f"; done`
- [ ] Commit messages follow Conventional Commits

## Milestone

Closes # · Targets milestone: v0.?
