#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Functional (no-prompt) API for pyIGRF.

Provides a simple function to compute geomagnetic field components and
optionally derived quantities, without any interactive inputs or file output.
"""

import os
from typing import Any, Dict

import numpy as np
from scipy import interpolate

import igrf_utils as iut


def compute_igrf(
    height_m,
    lat_deg,
    lon_deg,
    dyear,
    igrf_gen=14,
    outputs=("XYZ",),
):
    """
    Compute IGRF main field and optional derived quantities.

    Parameters
    ----------
    height_m : scalar or array-like
        Geodetic altitude(s) in meters above the WGS-84 ellipsoid.
    lat_deg : scalar or array-like
        Geodetic latitude(s) in degrees (north positive, south negative).
    lon_deg : scalar or array-like
        Geodetic longitude(s) in degrees (east positive, west negative).
    dyear : scalar or array-like
        Decimal year(s), e.g. 2020.25.
    igrf_gen : int, optional
        IGRF generation number (1..14). Default is 14.
    outputs : iterable of str, optional
        Requested outputs. Supported: "XYZ", "DHIF", "SV", "SV_DHIF".
        Default: ("XYZ",)

    Returns
    -------
    result : dict
        Dictionary containing requested outputs:
        - "XYZ": ndarray (..., 3) of X, Y, Z in nT
        - "DHIF": ndarray (..., 4) of D (deg), H (nT), I (deg), F (nT)
        - "SV": ndarray (..., 3) of dX, dY, dZ in nT/yr
        - "SV_DHIF": ndarray (..., 4) of dD (arcmin/yr), dH (nT/yr),
          dI (arcmin/yr), dF (nT/yr)
    """

    # Normalize outputs request
    if isinstance(outputs, str):
        outputs = (outputs,)
    outputs = tuple(o.upper() for o in outputs)

    # Broadcast inputs
    height_m = np.asarray(height_m, dtype=float)
    lat_deg = np.asarray(lat_deg, dtype=float)
    lon_deg = np.asarray(lon_deg, dtype=float)
    dyear = np.asarray(dyear, dtype=float)

    b = np.broadcast(height_m, lat_deg, lon_deg, dyear)
    height_m = np.broadcast_to(height_m, b.shape)
    lat_deg = np.broadcast_to(lat_deg, b.shape)
    lon_deg = np.broadcast_to(lon_deg, b.shape)
    dyear = np.broadcast_to(dyear, b.shape)

    # Convert to colatitude and geocentric radius
    colat = 90.0 - lat_deg
    alt_km = height_m / 1000.0
    radius_km, colat_gc, sd, cd = iut.gg_to_geo(alt_km, colat)

    # Load coefficients
    module_dir = os.path.dirname(os.path.abspath(__file__))
    igrf_file = os.path.join(module_dir, "SHC_files", f"IGRF{int(igrf_gen)}.SHC")
    igrf = iut.load_shcfile(igrf_file, None)

    # Interpolate coefficients to requested dates
    f = interpolate.interp1d(igrf.time, igrf.coeffs, fill_value="extrapolate")
    coeffs = f(dyear)

    # Main field synthesis (geocentric)
    Br, Bt, Bp = iut.synth_values(coeffs.T, radius_km, colat_gc, lon_deg,
                                  igrf.parameters["nmax"])

    # Secular variation (SV) coefficients
    epoch = (dyear - 1900) // 5
    epoch_start = epoch * 5
    coeffs_sv = f(1900 + epoch_start + 1) - f(1900 + epoch_start)
    Brs, Bts, Bps = iut.synth_values(coeffs_sv.T, radius_km, colat_gc, lon_deg,
                                     igrf.parameters["nmax"])

    # Coeffs at start of epoch for non-linear SV
    coeffsm = f(1900 + epoch_start)
    Brm, Btm, Bpm = iut.synth_values(coeffsm.T, radius_km, colat_gc, lon_deg,
                                     igrf.parameters["nmax"])

    # Convert to X, Y, Z (geocentric)
    X = -Bt
    Y = Bp
    Z = -Br
    dX = -Bts
    dY = Bps
    dZ = -Brs
    Xm = -Btm
    Ym = Bpm
    Zm = -Brm

    # Rotate back to geodetic coordinates
    t = X
    X = X * cd + Z * sd
    Z = Z * cd - t * sd
    t = dX
    dX = dX * cd + dZ * sd
    dZ = dZ * cd - t * sd
    t = Xm
    Xm = Xm * cd + Zm * sd
    Zm = Zm * cd - t * sd

    result: Dict[str, Any] = {}

    if "XYZ" in outputs:
        result["XYZ"] = np.stack((X, Y, Z), axis=-1)
    if "SV" in outputs:
        result["SV"] = np.stack((dX, dY, dZ), axis=-1)

    if "DHIF" in outputs or "SV_DHIF" in outputs:
        dec, hoz, inc, eff = iut.xyz2dhif(X, Y, Z)
        if "DHIF" in outputs:
            result["DHIF"] = np.stack((dec, hoz, inc, eff), axis=-1)

    if "SV_DHIF" in outputs:
        decs, hozs, incs, effs = iut.xyz2dhif_sv(Xm, Ym, Zm, dX, dY, dZ)
        result["SV_DHIF"] = np.stack((decs, hozs, incs, effs), axis=-1)

    return result


def compute_igrf_xyz(height_m, lat_deg, lon_deg, dyear, igrf_gen=14):
    """
    MATLAB-friendly wrapper that returns only XYZ as a float64 ndarray (..., 3).
    """
    result = compute_igrf(
        height_m=height_m,
        lat_deg=lat_deg,
        lon_deg=lon_deg,
        dyear=dyear,
        igrf_gen=igrf_gen,
        outputs=("XYZ",),
    )
    return np.asarray(result["XYZ"], dtype=np.float64)


def compute_igrf_all(height_m, lat_deg, lon_deg, dyear, igrf_gen=14):
    """
    MATLAB-friendly wrapper with fixed positional outputs.

    Returns
    -------
    XYZ : ndarray (..., 3)
        X, Y, Z in nT
    DHIF : ndarray (..., 4)
        D (deg), H (nT), I (deg), F (nT)
    SV : ndarray (..., 3)
        dX, dY, dZ in nT/yr
    SV_DHIF : ndarray (..., 4)
        dD (arcmin/yr), dH (nT/yr), dI (arcmin/yr), dF (nT/yr)
    """
    result = compute_igrf(
        height_m=height_m,
        lat_deg=lat_deg,
        lon_deg=lon_deg,
        dyear=dyear,
        igrf_gen=igrf_gen,
        outputs=("XYZ", "DHIF", "SV", "SV_DHIF"),
    )
    xyz = np.asarray(result["XYZ"], dtype=np.float64)
    dhif = np.asarray(result["DHIF"], dtype=np.float64)
    sv = np.asarray(result["SV"], dtype=np.float64)
    sv_dhif = np.asarray(result["SV_DHIF"], dtype=np.float64)
    return xyz, dhif, sv, sv_dhif
