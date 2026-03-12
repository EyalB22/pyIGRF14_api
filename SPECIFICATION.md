# Project Specification

## Objective

Build a server module based on the `pyIGRF` computational core so the same magnetic-field backend can be embedded and reused across multiple client applications.

## Problem Statement

Different host applications (for example MATLAB, C#, and other clients) should not reimplement IGRF computation logic independently. The project should provide a single backend module with consistent behavior, units, and outputs.

## Target Outcome

1. A reusable server-facing module that exposes the `pyIGRF` computation through a stable interface.
2. Compatibility with multiple client environments through thin adapters/wrappers.
3. Numerical consistency across clients by centralizing the compute path.

## Scope

In scope:
1. Keep one canonical compute implementation in Python.
2. Add server and integration interfaces without changing physics/math unless explicitly requested.
3. Provide parity tests that validate wrapper/server outputs against the canonical compute path.

Out of scope:
1. Rewriting magnetic model computations in each client platform.
2. Introducing model behavior changes without explicit approval and test coverage.

## Design Principles

1. Single source of truth for computations (`compute_igrf` and core utilities).
2. Thin integration layers (MATLAB/C#/service adapters should avoid business logic duplication).
3. Stable and explicit I/O contract (units, dimensions, and output ordering).
4. Reproducibility and traceability through automated tests and version control.

