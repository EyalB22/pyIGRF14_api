% Compare MATLAB igrfmagm against Python pyIGRF_api backend.
% Run from MATLAB.
%
% Preconditions:
% 1) MATLAB has Aerospace Toolbox (igrfmagm available)
% 2) Python env has numpy + scipy installed
% 3) pyIGRF_api.py exists in project root

clear; clc;

%% Configuration
projectRoot = 'C:\Users\eyalb\Desktop\pyIGRF14\pyIGRF14';
igrfGeneration = int32(13);
height_m = 0.0;  % sea level test

% Years constrained to 2025 and earlier.
testYears = [1900.0, 1950.0, 2000.0, 2015.5, 2020.0, 2025.0];

% Capitals across hemisphere quadrants (NE, NW, SE, SW).
capitals = struct( ...
    'Name', {'Tokyo', 'New Delhi', 'Washington DC', 'Ottawa', ...
             'Canberra', 'Wellington', 'Santiago', 'Buenos Aires'}, ...
    'Lat',  { 35.6762,  28.6139,      38.9072,       45.4215, ...
             -35.2809, -41.2866,     -33.4489,      -34.6037}, ...
    'Lon',  {139.6503,  77.2090,     -77.0369,      -75.6972, ...
             149.1300, 174.7756,     -70.6693,      -58.3816} ...
);

% Acceptance thresholds (tune if needed for your MATLAB release).
absTolXYZ_nT = 1.0;      % max absolute component diff
rmsTolXYZ_nT = 0.5;      % RMS diff across XYZ components

%% Checks
if exist('igrfmagm', 'file') ~= 2
    error('igrfmagm not found. Aerospace Toolbox is required.');
end

if count(py.sys.path, projectRoot) == 0
    insert(py.sys.path, int32(0), projectRoot);
end

if ~exist('igrf_proj_path', 'var')
    igrf_proj_path = addpath(genpath('C:\Users\eyalb\Desktop\pyIGRF14\pyIGRF14'));
end

if pyenv().Status == "NotLoaded"
    pyenv(ExecutionMode="OutOfProcess");
end

mod = py.importlib.import_module('pyIGRF_api');
py.importlib.reload(mod);

%% Run comparisons
nCaps = numel(capitals);
nYears = numel(testYears);
nRows = nCaps * nYears;

City = strings(nRows, 1);
Year = zeros(nRows, 1);
Lat = zeros(nRows, 1);
Lon = zeros(nRows, 1);
MaxAbsDiff_nT = zeros(nRows, 1);
RmsDiff_nT = zeros(nRows, 1);
Pass = false(nRows, 1);

row = 0;
for i = 1:nCaps
    for j = 1:nYears
        row = row + 1;
        lat = capitals(i).Lat;
        lon = capitals(i).Lon;
        yr = testYears(j);

        % MATLAB reference
        [xyzMatlab, ~, ~, ~, ~, ~, ~, ~, ~, ~] = igrfmagm( ...
            height_m, lat, lon, yr, igrfGeneration);

        % Python backend
        xyzPython = double(mod.compute_igrf_xyz( ...
            height_m, lat, lon, yr, igrfGeneration));
        xyzPython = reshape(xyzPython, 1, 3);

        diffXYZ = xyzPython - xyzMatlab;
        maxAbsDiff = max(abs(diffXYZ));
        rmsDiff = sqrt(mean(diffXYZ.^2));

        City(row) = string(capitals(i).Name);
        Year(row) = yr;
        Lat(row) = lat;
        Lon(row) = lon;
        MaxAbsDiff_nT(row) = maxAbsDiff;
        RmsDiff_nT(row) = rmsDiff;
        Pass(row) = (maxAbsDiff <= absTolXYZ_nT) && (rmsDiff <= rmsTolXYZ_nT);
    end
end

results = table(City, Year, Lat, Lon, MaxAbsDiff_nT, RmsDiff_nT, Pass);
results = sortrows(results, {'MaxAbsDiff_nT', 'RmsDiff_nT'}, {'descend', 'descend'});

%% Report
fprintf('\nComparison: MATLAB igrfmagm vs Python pyIGRF_api.compute_igrf_xyz\n');
fprintf('Generation: IGRF-%d | Test height: %.1f m | Cases: %d\n', ...
    igrfGeneration, height_m, nRows);
fprintf('Max abs tol: %.3f nT | RMS tol: %.3f nT\n\n', absTolXYZ_nT, rmsTolXYZ_nT);

disp(results(1:min(20, height(results)), :));

overallPass = all(results.Pass);
globalMaxAbs = max(results.MaxAbsDiff_nT);
globalMaxRms = max(results.RmsDiff_nT);

fprintf('\nGlobal max abs diff: %.6f nT\n', globalMaxAbs);
fprintf('Global max RMS diff: %.6f nT\n', globalMaxRms);
fprintf('Overall pass: %d\n', overallPass);

if ~overallPass
    warning('One or more test cases exceeded tolerance.');
end

