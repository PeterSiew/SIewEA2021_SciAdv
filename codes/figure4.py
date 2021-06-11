import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import datetime as dt

import read_tools as rt
import bootstrap_tools as bt
import correlation_tools as ct
import plotting_tools as pt

import figure4

if __name__ == "__main__":

	mvars = ['BKSICE', 'BKSICE', 'URALS']; mvar_names=['ice', 'ice', 'USLP']
	main_mons = ['Nov', 'Nov', 'Nov']
	com_vars = ['NAOSLPbased', 'BKSTHF', 'NAOSLPbased']; com_vars_name = ['NAO','THF','NAO']
	com_mons = [['Nov', 'Dec', 'Jan', 'Feb'], ['Nov', 'Dec'], ['Jan', 'Feb']]
	com_methods = ['old','select_lowest_highest_by_months','select_lowest_highest_by_months']

	panels = ['A', 'B', 'C']
	obs_grids, boxplot_grids = [], []
	for i, panel in enumerate(panels):
		plotting_obs, plotting_boxplot = figure4.getting_plotting_data(mvars[i], main_mons[i], com_vars[i], com_mons[i], com_methods[i])
		obs_grids.append(plotting_obs)
		boxplot_grids.append(plotting_boxplot)
		
	figure4.plotting_data(obs_grids, boxplot_grids, mvars, mvar_names, main_mons,  com_vars, com_vars_name, com_mons, com_methods)

def getting_plotting_data(mvar, main_mon, com_var, com_mon, com_method):

	indices = ['NAOSLPbased', 'BKSTHF', 'URALS', 'PCH50', 'BKSICE']
	indices_label = ['NAO', 'Turbulent heat flux', 'Urals sea level pressure', 'Polar cap height at 50 hPa']
	mons = ['Oct', 'Nov', 'Dec', 'Jan', 'Feb']
	resolution='monthly'
	
	random_ss = 10000; sample_size=100
	random_sampling = True
	fn_add = 'Rfig6'

	models =['20CRv3', 'CCSM4','CESM1-WACCM','CESM2','CESM2-WACCM', 'ACCESS-CM2','ACCESS-ESM1-5','BCC-ESM1','CAMS-CSM1-0','CNRM-ESM2-1','CanESM5',
			'EC-Earth3-Veg','FGOALS-g3','INM-CM5-0','IPSL-CM6A-LR','MIROC6','MPI-ESM1-2-HR','MPI-ESM1-2-LR','MRI-ESM2-0','NorESM2-LM', 'NorESM2-MM']
	mts = ['reanalysis']*1 + ['CMIP5_PI']*2 + ['CMIP6_PI']*18

	time_MS = {m: False for m in models}
	time2pd1700 = {m: False for m in models}

	corr_indices = ['BKSICE', 'BKSTHF', 'URALS', 'PCH50', 'NAOSLPbased']; corr_indices_name = ['ice', 'THF', 'USLP', 'PCH50', 'NAO']
	corr_months = [['Nov'],  ['Nov', 'Dec'], ['Nov'], ['Dec', 'Jan'], ['Jan', 'Feb']]


	###################################################################################################

	tsds_obs, corr_obs, tsds_model_long, corr_model_long, tsds_model_samples, corr_model_samples = rt.obtain_era5_piruns_correlations(main_mon=main_mon, mons=mons,
											mvar=mvar, resolution=resolution, mts=mts, models=models,time_MS=time_MS, time2pd1700=time2pd1700, indices=indices,
											random_sampling=random_sampling, random_ss=random_ss, drop_mainvar=False)
	member_close, member_far = bt.obtain_member_close_far(mts=mts, models=models,corr_obs=corr_obs,corr_model_samples=corr_model_samples,resolution=resolution,
								com_var=com_var, com_mon=com_mon, com_method=com_method, sample_size=sample_size)


	# Make the plotting here
	# setup (A) - Bootstapped based on NAO
	single_close = {model+'_close':[] for model in models}
	single_far = {model+'_far':[] for model in models}
	single_row = {**single_close, **single_far}
	for model in models:
		for corr_index, corr_month in zip(corr_indices, corr_months):
			aa = corr_model_samples[model].correlation.sel(indices=corr_index).sel(mons=corr_month).sel(en=member_close[model]).values.flatten()
			single_row[model+'_close'].append(aa)
			bb = corr_model_samples[model].correlation.sel(indices=corr_index).sel(mons=corr_month).sel(en=member_far[model]).values.flatten()
			single_row[model+'_far'].append(bb)

	### Find the multi-model mean from the model
	single_row_new = {'20CRv3_close':None, 'MMM_close':[], '20CRv3_far':None, 'MMM_far':[]}
	for i, corr_index in enumerate(corr_indices):
		temp = np.array([single_row[m+'_close'][i] for m in models[1:]]).flatten()
		single_row_new['MMM_close'].append(temp)
		temp = np.array([single_row[m+'_far'][i] for m in models[1:]]).flatten()
		single_row_new['MMM_far'].append(temp)

	single_row_new['20CRv3_close'] = single_row['20CRv3_close']
	single_row_new['20CRv3_far'] = single_row['20CRv3_far']

	#boxplot_grids = [single_row_new]
	obs_corrs = []
	for corr_index, corr_month in zip(corr_indices, corr_months):
		obs_corr = corr_obs.correlation.sel(indices=corr_index).sel(mons=corr_month).mean(dim='mons').values
		obs_corrs.append(obs_corr)
	
	return obs_corrs, single_row_new


def plotting_data(obs_grids, boxplot_grids, mvars, mvar_names, main_mons,  com_vars, com_vars_name, com_mons, com_methods):

	# Need to improve later
	corr_indices = ['BKSICE', 'BKSTHF', 'URALS', 'PCH50', 'NAOSLPbased']; corr_indices_name = ['ice', 'THF', 'USLP', 'PCH50', 'NAO']
	corr_months = [['Nov'],  ['Nov', 'Dec'], ['Nov'], ['Dec', 'Jan'], ['Jan', 'Feb']]

	rows = len(obs_grids)

	xlabels =  range(len(obs_grids[0]))
	boxplot_types = [*boxplot_grids[0]]

	### Real Plotting
	fname = 'figure4'
	plt.close()
	fig, ax_all = plt.subplots(rows, 1, figsize=(6, 7))

	btcolors = {}; btcolors['20CRv3_close']='gray'; btcolors['20CRv3_far']='gray'; btcolors['MMM_close']='red'; btcolors['MMM_far']='red'
	bpcolors_row = {bt: btcolors[bt] for bt in boxplot_types}
	bpcolors_grids = [bpcolors_row] * rows
	xadjust = [-0.12,0,0.12,0.24]
	errorbar_marker = ['o', 'x']
	errorbar_marker = ['o', 'o' ,'x', 'x']

	lines = obs_grids
	linescolors = ['black'] * rows
	xadjust_line=-0.24
	bp_full = {bt:True for bt in boxplot_types}
	pt.leadlag_grid_plotting(rows, xlabels, pltf=fig, ax_all=ax_all, sig_line=True, fig_xsize=6, legend_element=None, boxplots=boxplot_grids, bpcolors=bpcolors_grids,
						xadjust=xadjust, real_boxplot=False, eb_marker=errorbar_marker, lines=lines,linescolors=linescolors, xadjust_line=xadjust_line, eb_full=bp_full)

	# Plot the observations
	#ax_all.plot(np.arange(len(xlabels))-0.2, obs_corrs, marker='o', linestyle='None', color='black')

	title_ycor = [1.1, 1.1, 1]
	ABCD = ['A', 'B', 'C', 'D']
	for i, ax in enumerate(ax_all):
		title_row = r'Partitioning by %s$_\mathrm{%s}$-%s$_\mathrm{%s}$ correlations'%(mvar_names[i], main_mons[i], com_vars_name[i], '-'.join([com_mons[i][0],com_mons[i][-1]]))
		ax.set_ylim(-0.91,0.91)
		#ax.set_xlim(-0.4, 6)
		ax.set_ylabel('Correlation')
		ax.set_yticks([-0.6,-0.3,0,0.3,0.6])
		ax.annotate(r'$\bf{(%s)}$'%ABCD[i] + ' ' + title_row, xy=(0,title_ycor[i]), xycoords='axes fraction')
		xlabel_full = [r'%s$_\mathrm{%s}$'%(mvar_names[i], main_mons[i]) +'\n'+ '%s$_\mathrm{%s}$'%(j, '/'.join(k)) for j, k in zip(corr_indices_name, corr_months)]
		if i in [0,1]:
			xlabel_full[0] = ''
		if i == 2:
			xlabel_full[2] = ''
		ax.set_xticks(xlabels)
		ax.set_xticklabels(xlabel_full)
	ax_all[0].tick_params(axis="x", pad=-10) # more negative, the xtick and labels go further upwards
	ax_all[1].tick_params(axis="x", pad=-10) # more negative, the xtick and labels go further upwards

	if True:
		# For plotting the legend. Create a fake one
		obs = matplotlib.lines.Line2D([0],[0],marker='o', linestyle='None', color='black', lw=2)
		aa = ax_all[-1].errorbar(0,-100, yerr=[0], fmt='o', color=btcolors['20CRv3_close'], marker='o', markersize=4)
		bb = ax_all[-1].errorbar(0,-100, yerr=[0], fmt='x', color=btcolors['20CRv3_far'], marker='x', markersize=4)
		cc = ax_all[-1].errorbar(0,-100, yerr=[0], fmt='o', color=btcolors['MMM_close'], marker='o', markersize=4)
		dd = ax_all[-1].errorbar(0,-100, yerr=[0], fmt='x', color=btcolors['MMM_far'], marker='x', markersize=4)
		legend=ax_all[-1].legend(handles=[obs, aa, bb, cc, dd], labels=['ERA5', '20CRv3', '20CRv3', 'CMIP5&6', 'CMIP5&6'], ncol=5, 
											loc='lower left',bbox_to_anchor=(-0.10, -0.7), frameon=False, fontsize=10, columnspacing=0.2, handletextpad=0.07)

	plt.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=None, hspace=0.5)
	plt.savefig('./%s_%s.png' %(dt.date.today(), fname), bbox_inches='tight', dpi=300)
