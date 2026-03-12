% --- Minimal MATLAB -> Python IGRF test ---

% 1) Point MATLAB to a Python that has numpy + scipy installed
pe = pyenv;
if pe.Status == "NotLoaded"
    % Optionally set Version="C:\Path\To\python.exe"
    pyenv(ExecutionMode="OutOfProcess");
end

% 2) Add project root so MATLAB can import pyIGRF_api.py
projectRoot = 'C:\Users\eyalb\Desktop\pyIGRF14\pyIGRF14';
if count(py.sys.path, projectRoot) == 0
    insert(py.sys.path, int32(0), projectRoot);
end

% 3) Import module
mod = py.importlib.import_module('pyIGRF_api');
py.importlib.reload(mod);  % helpful while iterating

% 4) Test call (scalar input)
height_m = 100.0;
lat_deg = 32.1;
lon_deg = 34.8;
dyear = 2026;
igrf_gen = int32(14);

% Fixed MATLAB-friendly outputs:
out = mod.compute_igrf_all(height_m, lat_deg, lon_deg, dyear, igrf_gen);

% 5) Convert Python return values to MATLAB doubles
XYZ     = double(out{1});   % [X Y Z] nT
DHIF    = double(out{2});   % [D H I F]
SV      = double(out{3});   % [dX dY dZ]
SV_DHIF = double(out{4});   % [dD dH dI dF]

disp('XYZ (nT):'); disp(XYZ)
disp('DHIF:'); disp(DHIF)
disp('SV (nT/yr):'); disp(SV)
disp('SV_DHIF:'); disp(SV_DHIF)
