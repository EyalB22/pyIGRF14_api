#!/usr/bin/env python3
"""
Project REPL launcher.

Run:
    python repl.py
"""

import code

import numpy as np

from pyIGRF_api import compute_igrf, compute_igrf_all, compute_igrf_xyz


banner = """pyIGRF project REPL
Loaded names:
  - np
  - compute_igrf
  - compute_igrf_xyz
  - compute_igrf_all

Example:
  compute_igrf_xyz(0, 32.0, 35.0, 2025.5)
"""

namespace = {
    "np": np,
    "compute_igrf": compute_igrf,
    "compute_igrf_xyz": compute_igrf_xyz,
    "compute_igrf_all": compute_igrf_all,
}

code.interact(banner=banner, local=namespace)
