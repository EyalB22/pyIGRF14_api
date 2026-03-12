#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys

import numpy as np
from numpy.testing import assert_allclose
from scipy import interpolate

# Ensure project root imports resolve when tests are run from the tests folder.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import igrf_utils as iut
from pyIGRF_api import compute_igrf, compute_igrf_all, compute_igrf_xyz


def _original_pipeline(height_m, lat_deg, lon_deg, dyear, igrf_gen=14):
    """Replicate the computation path in pyIGRF.py without CLI I/O."""
    height_m = np.asarray(height_m, dtype=float)
    lat_deg = np.asarray(lat_deg, dtype=float)
    lon_deg = np.asarray(lon_deg, dtype=float)
    dyear = np.asarray(dyear, dtype=float)

    b = np.broadcast(height_m, lat_deg, lon_deg, dyear)
    height_m = np.broadcast_to(height_m, b.shape)
    lat_deg = np.broadcast_to(lat_deg, b.shape)
    lon_deg = np.broadcast_to(lon_deg, b.shape)
    dyear = np.broadcast_to(dyear, b.shape)

    # geodetic -> geocentric conversion, same as io_options -> pyIGRF flow
    colat = 90.0 - lat_deg
    alt_km = height_m / 1000.0
    alt_gc, colat_gc, sd, cd = iut.gg_to_geo(alt_km, colat)

    igrf_file = f"./SHC_files/IGRF{int(igrf_gen)}.SHC"
    igrf = iut.load_shcfile(igrf_file, None)
    f = interpolate.interp1d(igrf.time, igrf.coeffs, fill_value="extrapolate")

    coeffs = f(dyear)
    Br, Bt, Bp = iut.synth_values(coeffs.T, alt_gc, colat_gc, lon_deg,
                                  igrf.parameters["nmax"])

    epoch = (dyear - 1900) // 5
    epoch_start = epoch * 5
    coeffs_sv = f(1900 + epoch_start + 1) - f(1900 + epoch_start)
    Brs, Bts, Bps = iut.synth_values(coeffs_sv.T, alt_gc, colat_gc, lon_deg,
                                     igrf.parameters["nmax"])

    coeffsm = f(1900 + epoch_start)
    Brm, Btm, Bpm = iut.synth_values(coeffsm.T, alt_gc, colat_gc, lon_deg,
                                     igrf.parameters["nmax"])

    X = -Bt
    Y = Bp
    Z = -Br
    dX = -Bts
    dY = Bps
    dZ = -Brs
    Xm = -Btm
    Ym = Bpm
    Zm = -Brm

    # rotate geocentric -> geodetic
    t = X
    X = X * cd + Z * sd
    Z = Z * cd - t * sd
    t = dX
    dX = dX * cd + dZ * sd
    dZ = dZ * cd - t * sd
    t = Xm
    Xm = Xm * cd + Zm * sd
    Zm = Zm * cd - t * sd

    dec, hoz, inc, eff = iut.xyz2dhif(X, Y, Z)
    decs, hozs, incs, effs = iut.xyz2dhif_sv(Xm, Ym, Zm, dX, dY, dZ)

    return {
        "XYZ": np.stack((X, Y, Z), axis=-1),
        "DHIF": np.stack((dec, hoz, inc, eff), axis=-1),
        "SV": np.stack((dX, dY, dZ), axis=-1),
        "SV_DHIF": np.stack((decs, hozs, incs, effs), axis=-1),
    }


def test_compute_igrf_parity_scalar():
    expected = _original_pipeline(
        height_m=150.0,
        lat_deg=48.5,
        lon_deg=-123.2,
        dyear=2024.25,
        igrf_gen=14,
    )
    found = compute_igrf(
        height_m=150.0,
        lat_deg=48.5,
        lon_deg=-123.2,
        dyear=2024.25,
        igrf_gen=14,
        outputs=("XYZ", "DHIF", "SV", "SV_DHIF"),
    )

    for key in ("XYZ", "DHIF", "SV", "SV_DHIF"):
        assert_allclose(found[key], expected[key], rtol=1e-12, atol=1e-12)


def test_compute_igrf_parity_array():
    expected = _original_pipeline(
        height_m=np.array([0.0, 200.0, 1200.0]),
        lat_deg=np.array([60.0, 10.0, -35.0]),
        lon_deg=np.array([-45.0, 90.0, 140.0]),
        dyear=np.array([1900.0, 2020.5, 2030.0]),
        igrf_gen=14,
    )
    found = compute_igrf(
        height_m=np.array([0.0, 200.0, 1200.0]),
        lat_deg=np.array([60.0, 10.0, -35.0]),
        lon_deg=np.array([-45.0, 90.0, 140.0]),
        dyear=np.array([1900.0, 2020.5, 2030.0]),
        igrf_gen=14,
        outputs=("XYZ", "DHIF", "SV", "SV_DHIF"),
    )

    for key in ("XYZ", "DHIF", "SV", "SV_DHIF"):
        assert_allclose(found[key], expected[key], rtol=1e-12, atol=1e-12)


def test_compute_igrf_xyz_wrapper():
    base = compute_igrf(
        height_m=np.array([100.0, 200.0]),
        lat_deg=np.array([40.0, -20.0]),
        lon_deg=np.array([10.0, 120.0]),
        dyear=np.array([2010.0, 2025.0]),
        outputs=("XYZ",),
    )
    wrapped = compute_igrf_xyz(
        height_m=np.array([100.0, 200.0]),
        lat_deg=np.array([40.0, -20.0]),
        lon_deg=np.array([10.0, 120.0]),
        dyear=np.array([2010.0, 2025.0]),
    )
    assert_allclose(wrapped, base["XYZ"], rtol=1e-12, atol=1e-12)


def test_compute_igrf_all_wrapper():
    base = compute_igrf(
        height_m=150.0,
        lat_deg=48.5,
        lon_deg=-123.2,
        dyear=2024.25,
        outputs=("XYZ", "DHIF", "SV", "SV_DHIF"),
    )
    xyz, dhif, sv, sv_dhif = compute_igrf_all(
        height_m=150.0,
        lat_deg=48.5,
        lon_deg=-123.2,
        dyear=2024.25,
    )
    assert_allclose(xyz, base["XYZ"], rtol=1e-12, atol=1e-12)
    assert_allclose(dhif, base["DHIF"], rtol=1e-12, atol=1e-12)
    assert_allclose(sv, base["SV"], rtol=1e-12, atol=1e-12)
    assert_allclose(sv_dhif, base["SV_DHIF"], rtol=1e-12, atol=1e-12)
