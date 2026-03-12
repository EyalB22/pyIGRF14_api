# Contributing

## Scope

This project provides IGRF magnetic-field computation with:
- an interactive CLI (`pyIGRF.py`)
- a programmatic API (`pyIGRF_api.py`)
- MATLAB integration support scripts (`tests/*.m`)

## Development Setup

From repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install pytest
```

## Local Validation

Required before opening a PR:

```powershell
python -m pytest tests\test_api_parity.py -q
```

## Pull Request Rules

1. Keep changes focused and minimal.
2. Describe behavior changes explicitly.
3. For numerical/process changes:
- include rationale
- include tests
- include expected impact/tolerance
4. Do not commit generated artifacts or environment folders.

## Coding Guidance

1. Do not duplicate core computation logic in multiple modules.
2. Prefer wrappers around `compute_igrf` for integration-specific APIs.
3. Preserve units and coordinate conventions in docstrings and comments.
4. Use module-relative SHC file paths, not working-directory-relative paths.

## Commit Message Suggestions

Use clear imperative messages, for example:
- `Add MATLAB-friendly API wrappers`
- `Fix SHC path resolution to be module-relative`
- `Add parity tests for API wrappers`

