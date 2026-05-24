# Security Policy

## Supported Versions

While Setlhare is pre-alpha (< 1.0), only the `main` branch receives
security fixes. Once we ship 1.0, the latest minor version on each
released major will be supported.

## Reporting a Vulnerability

**Do not open a public issue for security vulnerabilities.**

Instead, please report them privately by:

1. Using GitHub's **"Report a vulnerability"** feature in the Security tab
   of the repository, *or*
2. Emailing `security@setlhare-lang.org` (TODO: set up this address).

Please include:

- A description of the vulnerability
- Steps to reproduce
- The version / commit SHA you tested against
- Any suggested mitigation

We will acknowledge receipt within 72 hours and aim to provide a fix or
mitigation plan within 14 days for high-severity issues.

## Scope

In scope:

- The compiler, runtime, VM, and standard library
- The `spore` package manager
- The language server (LSP)

Out of scope (report upstream):

- Vulnerabilities in dependencies (Python, LLVM, Binaryen, etc.)
- Vulnerabilities in user code written *in* Setlhare
