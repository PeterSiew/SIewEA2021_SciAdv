Background
----------
This repository contains the code to construct Figures 2, 3 and 4 (the bootstrapping tests) in Siew et al. 2021

P. Y. F. Siew, C. Li, M. Ting, S. P. Sobolowski, Y. Wu, X. Chen, North Atlantic Oscillation in winter is largely insensitive to autumn Barents-Kara sea ice variability, Science Advances, 2021

Status
----------
More intructions and comments will be addeded. Suggestions are appreciated. Please send any questions to my email yu.siew@uib.no 

Data 
----------
The folder "timeseries_data" contains the time series used in the study. Time series include Barents-Kara sea ice index (BKSICE), turbulent heat flux over Barents-Kara sea (BKSTHF), sea level pressure over Urals (URALS), polar cap height at 50 hPa (PCH50) and NAO (NAOSLPbased). All time series are in monthly resolution. 

The ECMWF ERA5 reanalysis data are available from the Copernicus Climate Change Service (C3S) Climate Data Store: https://cds.climate.copernicus.eu/.

The NOAA-CIRES-DOE 20th Century Reanalysis V3 data are available from the NOAA Physical Sciences Laboratory (PSL): https://https://psl.noaa.gov/

CMIP5 and CMIP6 data are available from the Earth System Grid Federation: https://esgf-node.llnl.gov/projects/esgf-llnl/. 

CESM1-LENS data are available from the NCAR Climate Data Gateway: https://www.earthsystemgrid.org/. 

Codes
----------
Codes are written in Python. Libraries required are: numpy, xarray, scipy, matplotlib, pandas and datetime

reload_tools.py: tools for initializing and reading the time series.

bootstrap_tools.py: tools for reshuffling with replacement (i.e., the bootstrapping) and selecting the targeted bootstrapped samples.

correlation_tools.py: tools for calculating multiple correlations in a vectorized way (to minimize too many "for loops").

plotting_tools.py: tools for plotting the figures

figure2.py: constucting Figure 2 in the paper

figure3.py: constucting Figure 3 in the paper

figure4.py: constucting Figure 4 in the paper
