# Changelog

All notable changes to this project are documented in this file.

## [Unreleased]

### Added

- Non-interactive API in `pyIGRF_api.py` via `compute_igrf`.
- MATLAB-friendly wrapper APIs: `compute_igrf_xyz`, `compute_igrf_all`.
- API parity test suite in `tests/test_api_parity.py`.
- MATLAB comparison script `tests/matlab_compare_igrfmagm.m`.
- Minimal MATLAB call example `tests/small_matlab_call_example.m`.
- Project governance docs: `AGENTS.md`, `CONTRIBUTING.md`, and CI workflow.

### Changed

- SHC file loading in `pyIGRF_api.py` now resolves relative to module location, not current working directory.
