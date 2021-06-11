import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import datetime as dt

import read_tools as rt
import bootstrap_tools as bt
import correlation_tools as ct
import plotting_tools as pt

import figure3



if __name__ == "__main__":

	indices = ['NAOSLPbased', 'BKSTHF', 'URALS', 'PCH50', 'BKSICE']
	indices_label = ['NAO', 'Turbulent heat flux', 'Urals sea level pressure', 'Polar cap height at 50 hPa']
	mvar='BKSICE'; main_mon='Nov'
	mons=['Oct', 'Nov', 'Dec', 'Jan', 'Feb']
	resolution='monthly'
	com_var='NAOSLPbased'; com_mon = ['Nov', 'Dec', 'Jan', 'Feb']; com_method='old'
	random_sampling=True; random_ss = 10000; sample_size=100

	mts = ['CMIP6_PI', 'CMIP6_PI']
	models = ['CESM2', 'CESM2-WACCM']
	time_MS = {m: False for m in models} 
	time2pd1700 = {m: False for m in models} 
	#############################################################################################

	tsds_obs, corr_obs, tsds_model_long, corr_model_long,  tsds_model_samples, corr_model_samples = rt.obtain_era5_piruns_correlations(main_mon=main_mon, mons=mons,
											mvar=mvar, resolution=resolution, mts=mts, models=models,time_MS=time_MS, time2pd1700=time2pd1700, indices=indices,
											random_sampling=random_sampling, random_ss=random_ss)
	member_close, member_far = bt.obtain_member_close_far(mts=mts, models=models, corr_obs=corr_obs, corr_model_samples=corr_model_samples, resolution=resolution,
								com_var=com_var, com_mon=com_mon, com_method=com_method, sample_size=sample_size)

	figure3.plotting(member_close, member_far, corr_obs, corr_model_samples, vars_label=indices_label)

def plotting(member_close, member_far, corr_long_obs, corr_samples, fname='figure3', vars_label=None):

	models = [*corr_samples]
	vars = corr_samples[models[0]].indices.values 
	mons = corr_samples[models[0]].mons.values

	### Select the plotted 100 samples
	types = ['close', 'far']
	boxplot_types = [m+'_'+t for t in types for m in models] # type first and then models (i.e, close-A, close-B, close-C and then far-A far-B far-C)
	boxplots_grid = [{bt:None for bt in boxplot_types} for var in vars]
	for i, var in enumerate(vars):
		for m in models:
			boxplots_grid[i][m+'_close'] = [corr_samples[m].correlation.sel(indices=var).sel(mons=mon).sel(en=member_close[m]).values for mon in mons]
			boxplots_grid[i][m+'_far'] = [corr_samples[m].correlation.sel(indices=var).sel(mons=mon).sel(en=member_far[m]).values for mon in mons]
	# boxplot_type on each row
	# For each row, it is just like having 4 models as Fig. 1

	### Start plotting
	plt.close()
	fig, ax_all = plt.subplots(len(vars),1, figsize=(len(boxplot_types)*1.25, len(vars)*2))
	rows = len(vars)

	# Things that need to iterate at each rows
	colors = ['sandybrown', 'saddlebrown'] * len(types) # There two two types
	bpcolors_row = {bt: colors[i] for i, bt in enumerate(boxplot_types)}
	bpcolors = [bpcolors_row for var in vars]
	lines = [[corr_long_obs.correlation.sel(indices=var).sel(mons=mon).values for mon in mons] for var in vars]
	linescolors = ['black'] * len(vars)
	boxplot_range = {m:True for m in boxplot_types}

	xadjust_line=-0.21 # adjust the observations
	if False: # To overlapping the blue and rd
		xadjust = np.repeat(np.linspace(-len(models)*0.05, len(models)*0.05, len(models)),2) # To overlapping them
		zorder = [2, 1] * len(models) # blue, red, blue, red
	else: # Not overlapping
		xadjust = [-0.06,0.06,0.21,0.33]
	errorbar_marker = ['o', 'o' ,'x', 'x']

	pt.leadlag_grid_plotting(rows, mons, pltf=fig, ax_all=ax_all, sig_line=True, fig_xsize=None, legend_element=None,
									boxplots=boxplots_grid,bpcolors=bpcolors, xadjust=xadjust, real_boxplot=False, eb_marker=errorbar_marker,
										lines=lines,linescolors=linescolors, xadjust_line=xadjust_line, eb_full=boxplot_range)

	# For plotting the legend. Create a fake one
	obs = matplotlib.lines.Line2D([0],[0],marker='o', linestyle='None', color=linescolors[0], lw=2)
	aa = ax_all[0].errorbar(10,0, yerr=[0], fmt='o', color=colors[0], marker='o', markersize=4)
	bb = ax_all[0].errorbar(10,0, yerr=[0], fmt='o', color=colors[1], marker='o', markersize=4)
	cc = ax_all[0].errorbar(10,0, yerr=[0], fmt='o', color=colors[0], marker='x', markersize=4)
	dd = ax_all[0].errorbar(10,0, yerr=[0], fmt='o', color=colors[1], marker='x', markersize=4)
	legend=ax_all[0].legend(handles=[obs, aa, bb, cc, dd], labels=['ERA5', 'CESM2 most similar', 'CESM2-WACCM most similar', 'CESM2 least similar', 'CESM2-WACCM least similar'], ncol=2, 
										loc='lower left',bbox_to_anchor=(-0.19, -3.9), frameon=False, fontsize=10, columnspacing=0.10, handletextpad=0.07)

	title_ycor = 0.96
	ABCD = ['A', 'B', 'C', 'D']
	for i, ax in enumerate(ax_all):
		ax.set_ylim(-0.9,0.9)
		ax.set_xlim(-0.4, 4.6)
		ax.set_ylabel('Correlation')
		ax.set_yticks([-0.6,-0.3,0,0.3,0.6])
		ax.annotate(r'$\bf{(%s)}$'%ABCD[i] + ' ' + vars_label[i], xy=(0,title_ycor), xycoords='axes fraction')

	ax_all[3].tick_params(axis="x", pad=-15) # more negative, the xtick and labels go further upwards


	plt.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=None, hspace=0.1)
	plt.savefig('./%s_%s.png' %(dt.date.today(), fname), bbox_inches='tight', dpi=500)

