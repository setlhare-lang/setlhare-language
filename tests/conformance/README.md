# Conformance suite

Each subdirectory corresponds to a chapter of `docs/spec/`. Tests in
this suite must reference the spec section they codify.

Structure:

```
tests/conformance/
  01-lexical/
    comments.sl + comments.expected.json
    literals.sl + literals.expected.json
    ...
  02-syntax/
    func-decl.sl ...
  03-types/
    inference-let.sl ...
  ...
```

Each `*.sl` is a minimal program; each `*.expected.json` is the
expected output of `setlhare run` (stdout, exit code, diagnostics).

CI fails if a conformance test fails OR if a spec chapter has zero
tests covering it.

(TODO: implement the runner under `tests/test_conformance.py`.)
