import numpy as np
import xarray as xr
import bootstrap_tools as bt
import correlation_tools as ct

#import monthly_correlation as mc
#import rmse_histogram as rh


def obtain_era5_piruns_correlations(main_mon=None, mons=None, mvar=None, resolution=None, mts=None, models=None, time_MS=None, time2pd1700=None, indices=None, random_sampling=None, random_ss=None, scramble=False, rm10yrrm=False, drop_mainvar=True):

	"""
	This function is to 1) read the reanalysis/model timeseries, 2) carry out the bootstrapping test and 3) calculate the correlations
	frequency of the data
	"""

	### Getting the correlation data from ERA5
	model = 'Era5'; mt = 'reanalysis'
	cache_folder, yrs_r = which_cache_folder(model, mt)
	tsds_obs = read_raw_ts(resolution=resolution,select_yrs_mons=True,unit=False,st_yr=yrs_r[0],e_yr=yrs_r[1],model=model,mt=mt,indices=indices, rm10yrrm=rm10yrrm)

	if 'BKSICE' in indices:
		tsds_obs['BKSICE'] = tsds_obs['BKSICE']*-1
	corr_obs = ct.corr_leadlag_cal_function(tsds_obs, mons, mvar=mvar, mvar_mon=main_mon, resolution=resolution, drop_mainvar=drop_mainvar) 
		
	tsds_model_long, tsds_model_samples = {}, {}
	corr_model_long, corr_model_samples  = {}, {}

	### Getting the correlation data from the models
	for mt, model in zip(mts, models):

		# Read the yrs range for the model - select_yrs_mons must be True to fit the lead/lag
		cache_folder, yrs_r = which_cache_folder(model, mt)
		tsds_model_long[model] = read_raw_ts(indices=indices,resolution=resolution,select_yrs_mons=True,unit=False,st_yr=yrs_r[0],e_yr=yrs_r[1],model=model,
												mt=mt,time_MS=time_MS[model],time2pd1700=time2pd1700[model], rm10yrrm=rm10yrrm)
		if 'BKSICE' in indices:
			tsds_model_long[model]['BKSICE'] = tsds_model_long[model]['BKSICE'] * -1

		# Calculate the long-term correlations
		corr_model_long[model] = ct.corr_leadlag_cal_function(tsds_model_long[model], mons, mvar=mvar, mvar_mon=main_mon, resolution=resolution, drop_mainvar=drop_mainvar) 

		if random_sampling:
			# Do the random sampling for all PI_runs only
			tsds_model_samples[model] = bt.create_ensemble_tsds(tsds_model_long[model], trunk_type='random', random_ss=random_ss, seed=True, trunk_size=40,
																		rw_cache=False,model=model, mt=mt,resolution=resolution)
			# Calculate the correlations for samples
			corr_model_samples[model] = ct.corr_leadlag_cal_function(tsds_model_samples[model].drop('org_time'), mons, mvar=mvar, mvar_mon=main_mon, 
																	resolution=resolution, scramble=scramble, drop_mainvar=drop_mainvar)
		else:
			tsds_model_samples[model] = None
			corr_model_samples[model]  = None

	return tsds_obs, corr_obs, tsds_model_long, corr_model_long, tsds_model_samples, corr_model_samples

def read_raw_ts(indices=None,resolution='monthly',unit=False,data_type='anom',select_yrs_mons=True,model=None,mt=None,st_yr=None,e_yr=None, time_MS=False,time2pd1700=False,resample=None,rm10yrrm=False):

	"""
	This function reads the timeseries of the reanalysis/model data and have flexbility to perform some postprocessing (e.g., remove the 10-year running mean, resampling the
	frequency of the data
	"""

	cache_folder, yrs_range = which_cache_folder(model, mt)
	tsds = xr.Dataset()
	for i, ind in enumerate(indices):
		cache_path= cache_folder + 'ts/' + '%s_%s_%s_ts.nc' %(ind, resolution, data_type)
		tsda = xr.open_dataset(cache_path)
		varid = [i for i in tsda][0] # We assume there is onle one variable
		tsds[ind] = tsda[varid].squeeze() # Sometime the timeseries still have a dimension like lev
	if rm10yrrm: # Remove 10-year running mean (it must mean monthly data). This must be run before select_yrs_mons
		tsds = tt.remove_10yr_running_mean_monthly(tsds)
	if select_yrs_mons:
		mons_mask =tsds.time.dt.month.isin([10,11,12,1,2])
		tsds=tsds.sel(time=mons_mask).sel(time=slice('%s-10-01'%st_yr, '%s-02-28'%e_yr)) 
	if time2pd1700:
		tsds=ds_time_to_pd1700(tsds, resolution)
	if time_MS & (resolution=='monthly'): # Adjust the time so that they have the same time. Make the time consistent across models # Don't need to work on daily resolution
		newtime = time_reset(tsds.time.to_index())
		tsds = tsds.assign_coords(time = newtime)
	if resample in ['monthly', 'halfmonthly','pentad']:
		tsds=tsds_resample(tsds, resample)

	return tsds.compute()

def which_cache_folder(model, mt):

	"""
	This function indicates the position of the model/reanalysis data and the years that needed to be extracted
	"""

	yrs_range = {}

	if mt=='CMIP5_transient':
		cache_folder = '../timeseries_data/CMIP5/transient/' + model + '/'
		#yrs_range[model] = ('1861', '2100')
		yrs_range['CMIP5_1979to2019'] = ('1979', '2019')
		yrs_range['CESMLENS_1979to2019'] = ('1979','2019')

	elif mt=='CMIP5_PI':
		cache_folder = '../timeseries_data/CMIP5/PI/' + model + '/'
		yrs_range['CESM1-WACCM'] = ('1801','2200') # It's 1801 in order to match with the daily data 
		yrs_range['CCSM4'] = ('0100','1300') # The orignal CCSM has 1300 years

	elif mt=='CMIP6_PI':
		cache_folder = '../timeseries_data/CMIP6/PI/' + model + '/'
		yrs_range['ACCESS-CM2'] = ('0950','1449')
		yrs_range['ACCESS-ESM1-5'] = ('0101','1000')
		yrs_range['BCC-ESM1'] = ('1850','2300')
		yrs_range['CAMS-CSM1-0'] = ('2900','3399')
		yrs_range['CESM2'] = ('0001','1200')
		yrs_range['CESM2-WACCM'] = ('0001','0499')
		yrs_range['CNRM-ESM2-1'] = ('1850','2349')
		yrs_range['CanESM5'] = ('5201','6200')
		yrs_range['EC-Earth3-Veg'] = ('1850','2349')
		yrs_range['FGOALS-g3'] = ('0200','0899')
		yrs_range['INM-CM5-0'] = ('1996','3196')
		yrs_range['IPSL-CM6A-LR'] = ('1850','3849')
		yrs_range['MIROC6'] = ('3200','3999')
		yrs_range['MPI-ESM1-2-HR'] = ('1850','2349')
		yrs_range['MPI-ESM1-2-LR'] = ('1850','2849')
		yrs_range['MRI-ESM2-0'] = ('1850','2550')
		yrs_range['NorESM2-LM'] = ('1600','2100')
		yrs_range['NorESM2-MM'] = ('1200','1699') # SLP/NAO has 12 repeated data in year 1450 (in Nird) - I remove them by myself with Python
		#yrs_range['SAM0-UNICON'] = ('0001','0700') # ice has many repeated data in Nird - Bad data
		#yrs_range['UKESM1-0-LL'] = ('1960','2709') # ice has many repeated data in Nird - Bad data

	elif mt=='reanalysis':
		cache_folder = '../timeseries_data/' + model + '/'
		yrs_range['20CRv3'] = ('1901', '2015') # ('1836', '2015') # the ice has no variability prior to 1900
		yrs_range['Era5'] = ('1979', '2019') # After June 2020, the data are in expver5. Others are in expver 1
	
	elif mt is None:
		cache_folder, yrs_range = None, None
	else:
		raise ValueError('It must be one data type')

	return cache_folder, yrs_range[model]

