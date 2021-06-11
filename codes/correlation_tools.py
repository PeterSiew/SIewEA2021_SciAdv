import xarray as xr
from scipy import stats
import numpy as np

def corr_leadlag_cal_function(tsds, mons, mvar='BKSICE', mvar_mon='Nov', resolution='monthly',scramble=False, drop_mainvar=True):

	"""
	This function is to expand the data array with two additional dimensions (ie. months and variables)
	The aim is to calcualte regression/correlation with 1-step without looping by each grid, month and indices
	The calculation is done by the linregress_xarray function
	"""

	### November ts
	months_no = {'Oct':10, 'Nov':11, 'Dec':12, 'Jan':1, 'Feb':2, 'Mar':3}
	# 1: 1st-5st, 2: 6th-10th, 3:11th-15th, 4:16th-20th, 5:21th-25th, 6:26th-28/30/31th
	halfmonthly_day = {'1':1, '2':16}
	pentad_day = {'1':1, '2':6, '3':11, '4':16, '5':21, '6':26}

	if resolution == 'monthly':
		mask = tsds.time.dt.month == months_no[mvar_mon]
	elif resolution == 'halfmonthly':
		mask = (tsds.time.dt.month == months_no[mvar_mon[0:3]]) & (tsds.time.dt.day == halfmonthly_day[mvar_mon[-1]])
	elif resolution == 'pentad':
		mask = (tsds.time.dt.month == months_no[mvar_mon[0:3]]) & (tsds.time.dt.day == pentad_day[mvar_mon[-1]])
	x=tsds[mvar].sel(time=mask)
	# So that the tsds and x have the same time coordinate. Otherwise they cannot be propagate
	x= x.assign_coords(time=x.time.dt.year)

	# Remove the main variable from the tsds - not to calcualte the correlation between mainvar itself
	if drop_mainvar:
		tsds = tsds.drop(mvar)
	
	### Add the month as a new dimension for the indices (except mvar) for correlation calculation
	tsds_append = []
	for mon in mons:
		if resolution == 'monthly':
			mask = tsds.time.dt.month == months_no[mon]
		elif resolution == 'halfmonthly':
			mask = (tsds.time.dt.month == months_no[mon[0:3]]) & (tsds.time.dt.day == halfmonthly_day[mon[-1]])
		elif resolution == 'pentad':
			mask = (tsds.time.dt.month == months_no[mon[0:3]]) & (tsds.time.dt.day == pentad_day[mon[-1]])

		tsds_new=tsds.sel(time=mask)
		# Always assign the time axis of the time series to it.
		if x.time.shape == tsds_new.time.shape:
			tsds_new = tsds_new.assign_coords(time=x.time)
		else:
			raise ValueError('Please check line')
		tsds_append.append(tsds_new)
	tsds_mon_concat = xr.concat(tsds_append, dim='mons').assign_coords(mons=mons)
	tsds_mon_var_concat = tsds_mon_concat.to_array().rename({'variable':'indices'}) # once it is to_array(), the extra dimension is named "variables"

	# Load the results
	# x has a dimension of (en, time). tsds_mon_var_concat has dimention of (en, time, mon, indices). Resulsts will be calculated within each en (no crossing between en)
	results = linregress_xarray(tsds_mon_var_concat, x)
	
	return results

def linregress_xarray(y, x, null_hypo=0):
	# y is usually the 3darray
	# x is the timeseries
	# x and y should have the same time dimension
	# null_hypo is the null hypothsis of the slope 
	"""
	Input: Two xr.Datarrays of any dimensions with the first dim being time. Thus the input data could be a 1D time series, or for example, have three dimensions (time,lat,lon). 
	Output: Covariance, correlation, regression slope and intercept, p-value, and standard error on regression between the two datasets along their aligned time dimension.  
	Lag values can be assigned to either of the data, with lagx shifting x, and lagy shifting y, with the specified lag amount. 
	""" 
	#3. Compute data length, mean and standard deviation along time axis for further use: 
	size  = x.time.shape[0]
	xmean = x.mean(dim='time')
	ymean = y.mean(dim='time')
	xstd  = x.std(dim='time')
	ystd  = y.std(dim='time')

	#4. Compute covariance along time axis
	cov = ((x-xmean)*(y-ymean)).sum(dim='time', skipna=True)/size

	#5. Compute correlation along time axis
	cor = cov/(xstd*ystd)

	#6. Compute regression slope and intercept:
	slope     = cov/(xstd**2)
	intercept = ymean - xmean*slope  

	#7. Compute P-value and standard error
	#Compute t-statistics
	tstats = cor*np.sqrt(size-2)/np.sqrt(1-cor**2)
	stderr = slope/tstats

	if null_hypo!=0:
		# Calculate the standard error manually
		predicted_y = x*slope+intercept
		stderr_new = np.sqrt(((((predicted_y-y)**2).sum(dim='time'))/(size-2)) / (((x-xmean)**2).sum(dim='time')))
		tstats = (slope - null_hypo) / stderr_new

	pval = stats.t.sf(np.abs(tstats), size-2)*2
	pval = xr.DataArray(pval, dims=cor.dims, coords=cor.coords)

	results_ds = xr.Dataset()
	results_ds['covariance'] = cov
	results_ds['correlation'] = cor
	results_ds['slope'] = slope
	results_ds['intercept'] = intercept
	results_ds['pvalues'] = pval
	results_ds['standard_error'] = stderr

	#return cov,cor,slope,intercept,pval,stderr
	return results_ds
