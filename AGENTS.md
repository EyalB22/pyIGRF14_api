# AGENTS.md

This file defines repository context and guardrails for coding agents and contributors.

## Repository Purpose

`pyIGRF14_api` computes Earth magnetic field values from IGRF coefficient files.

Strategic project direction:
- Build an embeddable server module around the `pyIGRF` computational backend so multiple applications can use a single, consistent implementation.

Primary usage paths:
- CLI workflow: `pyIGRF.py`
- Programmatic API workflow: `pyIGRF_api.py`
- MATLAB interoperability scripts: `tests/*.m`

## Repository Map

- `pyIGRF.py`: interactive CLI entry point.
- `pyIGRF_api.py`: non-interactive API for scalar/array computation.
- `igrf_utils.py`: model loading, spherical harmonic synthesis, coordinate transforms, derived components.
- `io_options.py`: CLI input parsing and output formatting.
- `SHC_files/`: model coefficient data (`IGRF*.SHC`).
- `tests/test_api_parity.py`: parity tests for API and wrappers.
- `tests/matlab_compare_igrfmagm.m`: MATLAB comparison harness.
- `tests/small_matlab_call_example.m`: minimal MATLAB call example.

## Non-Negotiables

1. Preserve numerical process unless explicitly requested to change model behavior.
2. Any intentional numerical/process change must be accompanied by new tests and explicit note in `CHANGELOG.md`.
3. Keep unit conventions explicit:
- `height_m` in meters (API)
- lat/lon in decimal degrees
- decimal year input
- output `XYZ` in nT, SV in nT/yr, `D/I` in degrees, SV `D/I` in arcmin/yr
4. Keep SHC file resolution robust to working directory differences (module-relative paths).

## Coding Style

1. Prefer small, additive changes over broad refactors.
2. Add comments only where logic is non-obvious.
3. Avoid changing public function signatures without compatibility discussion.
4. Keep wrappers thin; keep core compute path centralized in `compute_igrf`.
5. Write code that is clean and concise.
6. Prefer vectorized NumPy operations over element-wise Python loops whenever practical.

## Validation Commands

Run from repository root:

```powershell
python -m pytest tests\test_api_parity.py -q
```

MATLAB interop validation (manual):

```matlab
run('C:\Users\eyalb\Desktop\pyIGRF14_api\pyIGRF14_api\tests\small_matlab_call_example.m')
run('C:\Users\eyalb\Desktop\pyIGRF14_api\pyIGRF14_api\tests\matlab_compare_igrfmagm.m')
```

## Known Constraints

1. `tests/tests_igrf13.py` and `tests/tests_igrf14.py` are legacy tests and are not part of CI gate yet.
2. MATLAB comparison scripts require MATLAB toolboxes and local Python interop configuration.
