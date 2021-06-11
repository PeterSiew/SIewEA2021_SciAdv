import numpy as np
import xarray as xr
import pandas as pd


def create_ensemble_tsds(tsds, trunk_type='random', random_ss=10000, seed=True, trunk_size=40, rw_cache=False, model=None, mt=None, resolution='monthly', replace=False):

	# Reshape by 5. It mush only have ONDJF
	mons_no = 5
	no_of_winters = tsds.time.shape[0] / mons_no
	winters_idx = np.repeat(np.arange(1,no_of_winters+1,dtype='int'), mons_no)
	tsds_new = tsds.assign_coords(time=winters_idx)
	winters_idx_set = list(set(winters_idx))
	#winters_idx = xr.DataArray(winters_idx,dims='time', coords={'time':tsds.time})

	### Create an observation-like timeseries
	if trunk_size==39:
		obs_tsds = pd.date_range(start='1979-10-01', end='2018-02-28', freq='MS')
	elif trunk_size==40:
		obs_tsds = pd.date_range(start='1979-10-01', end='2019-02-28', freq='MS')
	mask = obs_tsds.month.isin([10,11,12,1,2])
	manual_obs_ts=obs_tsds[mask]

	# Random --> draw 10,000 numbers from the total size. Create the timeseries
	if trunk_type=='random':
		tsds_en_list=[]
		for i in range(0, random_ss, 1):
			np.random.seed(i) if seed else None
			pick_years = np.random.choice(winters_idx_set, trunk_size, replace=replace)
			t_mask = tsds_new.time.isin(pick_years)
			tsds_en = tsds.sel(time=t_mask.values) # Only capture the index of the mask
			tsds_en['org_time'] = tsds_en.time
			tsds_en = tsds_en.assign_coords(time = manual_obs_ts)
			tsds_en_list.append(tsds_en)

	tsds_ens = xr.concat(tsds_en_list, dim='en')
	ensemble_r = np.arange(1, random_ss+1)
	tsds_ens = tsds_ens.assign_coords(en=ensemble_r)

	return tsds_ens

def obtain_member_close_far(mts=None, models=None, corr_obs=None, corr_model_samples=None, resolution=None, com_var=None,com_mon=None, com_method=None, sample_size=None):
	member_close, member_far= {}, {}
	if com_method in ['old', 'select_lowest_highest_by_months']:
		for model, mt in zip(models, mts):
			# memeber sorted as ascending order
			member_sorted = calculate_rmse(corr_obs, corr_model_samples[model], resolution=resolution,compared_var=com_var,compared_mons=com_mon,method=com_method)
			member_close[model] = member_sorted[0:sample_size]
			member_far[model] = member_sorted[-sample_size:]
	if com_method=='else':
		for model, mt in zip(models, mts):
			pass
	
	return member_close, member_far

def calculate_rmse(corr_long_obs, corr_samples, compared_var='NAO_SLPbased',resolution='monthly', compared_mons=['Dec', 'Jan', 'Feb'], method='old'):

	if method=='old':

		# The most traditional method.
		corr_obs_evolution = corr_long_obs.sel(indices=compared_var).sel(mons=compared_mons).correlation
		corr_en_evolution = corr_samples.sel(indices=compared_var).sel(mons=compared_mons).correlation
		# 1. Diff 2. square 3. mean 4. root
		rmse_close = (((corr_en_evolution - corr_obs_evolution)**2).mean(dim='mons'))**0.5
		members_sorted = rmse_close.sortby(rmse_close, ascending=True).en.values.tolist()

		# return rmse_close, members_sorted
		return members_sorted

	if method=='select_lowest_highest_by_months':
		# This method doesn't use the observations. It doesn't select member at the first stage
		corrs = corr_samples.sel(indices=compared_var).sel(mons=compared_mons).correlation
		# Average the correlations for each member. And then sort
		corrs = corrs.mean(dim='mons') # Even it only has 1 month, it can still be averaged - but simply no effect
		members_sorted = corrs.sortby(corrs, ascending=True).en.values.tolist()

		return members_sorted

	if method=="reverse_obs_least_similar": # Reverse the observed ice-NAO relationship and find the least similar group
		# This not is not used anymore

		corr_obs_evolution = corr_long_obs.sel(indices=compared_var).sel(mons=compared_mons).correlation
		corr_obs_evolution_reverse = corr_obs_evolution * -1
		# the rmse of across all members
		corr_en_evolution = corr_samples.sel(indices=compared_var).sel(mons=compared_mons).correlation
		# 1. Diff 2. square 3. mean 4. root
		rmse_close = (((corr_en_evolution - corr_obs_evolution)**2).mean(dim='mons'))**0.5
		rmse_far = (((corr_en_evolution - corr_obs_evolution_reverse)**2).mean(dim='mons'))**0.5
		member_close = rmse_close.sortby(rmse_close, ascending=True).en.values.tolist()
		member_far = rmse_far.sortby(rmse_far, ascending=True).en.values.tolist()

		return member_close, member_far
