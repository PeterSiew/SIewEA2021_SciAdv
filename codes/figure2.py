import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import datetime as dt

import read_tools as rt
import bootstrap_tools as bt
import correlation_tools as ct
import plotting_tools as pt

import figure2

if __name__ == "__main__":

	### Settings

	indices = ['NAOSLPbased', 'BKSICE']
	mvar = 'BKSICE'; main_mon='Nov'
	mons = ['Oct', 'Nov', 'Dec', 'Jan', 'Feb']
	resolution = 'monthly'

	mts_a = ['CMIP6_PI', 'CMIP6_PI']
	models_a = ['CESM2', 'CESM2-WACCM']

	models_b =['CCSM4', 'CESM1-WACCM', 'ACCESS-CM2','ACCESS-ESM1-5','BCC-ESM1','CAMS-CSM1-0','CNRM-ESM2-1','CanESM5','EC-Earth3-Veg','FGOALS-g3','INM-CM5-0',
				'IPSL-CM6A-LR','MIROC6','MPI-ESM1-2-HR','MPI-ESM1-2-LR','MRI-ESM2-0','NorESM2-LM', 'NorESM2-MM']
	mts_b = ['CMIP5_PI']*2 + ['CMIP6_PI']*(len(models_b)-2)

	mts_c = ['CMIP5_transient', 'CMIP5_transient']
	models_c = ['CESMLENS_1979to2019', 'CMIP5_1979to2019']

	time_MS = {m: False for m in models_a + models_b + models_c} 
	time2pd1700 = {m: False for m in models_a + models_b + models_c} 

	#######################################################################################################

	### Getting the correlation data for panel (A)
	mts = mts_a + mts_b 
	models = models_a + models_b
	random_sampling=True; random_ss = 10000
	tsds_obs, corr_obs, tsds_model_ab_long, corr_model_ab_long,  tsds_model_ab_samples, corr_model_ab_samples = rt.obtain_era5_piruns_correlations(main_mon=main_mon,
									mons=mons, mvar=mvar, resolution=resolution, mts=mts, models=models,time_MS=time_MS, time2pd1700=time2pd1700, indices=indices,
									random_sampling=random_sampling, random_ss=random_ss)
	mts = mts_c
	models = models_c
	random_sampling=False; random_ss = None 
	### Getting the correlation data for panel (B)
	__, __, tsds_model_c_long, corr_model_c_long, tsds_model_c_samples, corr_model_c_samples = rt.obtain_era5_piruns_correlations(main_mon=main_mon, mons=mons,
											mvar=mvar, resolution=resolution, mts=mts, models=models,time_MS=time_MS, time2pd1700=time2pd1700, indices=indices,
											random_sampling=random_sampling, random_ss=random_ss)
	# For the histotical runs - the corr_model_long is already grouped like they are corr_samples
	corr_model_samples = {**corr_model_ab_samples, **corr_model_c_long}

	# Start the plotting
	figure2.plotting(models_a, models_b, models_c, corr_obs, corr_model_ab_long, corr_model_samples)

def plotting(models_a, models_b, models_c, corr_long_obs, corr_long, corr_samples, fname='figure2'):

	mons = corr_long[models_a[0]].mons.values  
	indices = corr_long[models_a[0]].indices.values # Remove the correlation of ice, which is the last subject

	# Starting the plotting
	plt.close()
	fig, (ax1, ax2) = plt.subplots(2,1, figsize=((len(models_a)+1)*2, 4), sharex=True)

	# Extract the NCAR PI runs results
	models = models_a 
	boxplots_NCAR = {m:[corr_samples[m].correlation.sel(indices=indices[0]).sel(mons=mon).values for mon in mons] for m in models}
	# The dots reprensted the long-term correlation. here is the blackk horizontal line is the figure
	dots = {m:[corr_long[m].correlation.sel(indices=indices[0]).sel(mons=mon).values for mon in mons] for m in models_a}
	dots = [dots]

	# Aggreate the results (all other CMIP models) into one boxplot first
	models = models_b
	boxplots_others = {model:{mon:corr_samples[model].correlation.sel(indices=indices[0]).sel(mons=mon).values for mon in mons} for model in models}
	# Aggregate across all models
	boxplots_aggreated = [np.concatenate([boxplots_others[model][mon] for model in models]) for mon in mons]

	# Combine two NCAR and other PI runs boxplots
	boxplots = boxplots_NCAR
	boxplots['CMIP5&6'] = boxplots_aggreated
	boxplots = [boxplots]
	models = models_a + ['CMIP5&6']

	# Color of the boxplots
	colors_bp = ['sandybrown', 'saddlebrown', 'red']
	bpcolors = {m: colors_bp[i] for i,m  in enumerate(models)}
	bpcolors_row = [bpcolors] 

	# The observations. Lines is now the circle dots in the figure
	lines = [[corr_long_obs.correlation.sel(indices=indices[0]).sel(mons=mon).values for mon in mons]] 
	linescolors = ['black'] 

	# Others settings
	out_whis = [1,99]
	xadjust = [0, 0.17, 0.34] # xadjust of the boxplots
	xadjust_line = -0.17 # xadjust of the lien (now it is replaced by dots)
	rows = 1

	# Set the legend
	legend = [matplotlib.lines.Line2D([0],[0],marker='o', linestyle='None', color=linescolors[0], lw=2, label='ERA5')]+[matplotlib.patches.Patch(facecolor=bpcolors[m],edgecolor=bpcolors[m],label=m) for m in models]
	legend = ax1.legend(handles=legend, bbox_to_anchor=(-0.05, 1), ncol=4, loc='lower left', frameon=False,
										columnspacing=1.5, handletextpad=0.6)

	# Plot the (a) PI runs
	pt.leadlag_grid_plotting(rows, mons, boxplots=boxplots, bpcolors=bpcolors_row, lines=lines, linescolors=linescolors, sig_line=True, dots=dots,out_whis=out_whis, fn_add='new', pltf=fig, ax_all=[ax1], xadjust=xadjust, xadjust_line=xadjust_line)

	### plotting the Historical runs in (b)
	models = models_c
	colors_range = ['lightskyblue', 'royalblue']
	m_cols = {m: colors_range[i] for i,m  in enumerate(models)}

	boxplots = [{m:[corr_samples[m].correlation.sel(indices=indices[0]).sel(mons=mon).values for mon in mons] for m in models}]
	dots = [None]
	bpcolors = {m:m_cols[m] for m in models}
	bpcolors_row = [bpcolors]

	# Other settings for (b)
	model_labels = ['CESM1-LENS', 'CMIP5']
	out_whis = [1,99]
	xadjust = [0, 0.17] # xadjust of the boxplots
	xadjust_line = -0.17 # xadjust of the lien (now it is replaced by dots)
	rows = 1

	# use the observations already set in (a)
	legend = [matplotlib.lines.Line2D([0],[0],marker='o', linestyle='None', color=linescolors[0], lw=2, label='ERA5')]+[matplotlib.patches.Patch(facecolor=m_cols[m],edgecolor=m_cols[m],label=model_labels[i]) for i,m in enumerate(models)]
	legend = ax2.legend(handles=legend, bbox_to_anchor=(-0.05, 1), ncol=3, loc='lower left', frameon=False, columnspacing=1.5, handletextpad=0.6)

	pt.leadlag_grid_plotting(rows, mons, boxplots=boxplots, bpcolors=bpcolors_row, lines=lines, linescolors=linescolors, pltf=fig, ax_all=[ax2],sig_line=True,dots=dots,out_whis=out_whis,fn_add='', xadjust=xadjust,xadjust_line=xadjust_line)

	for ax in [ax1, ax2]:
		ax.set_xlim(-0.4, 4.5)
		ax.set_ylim(-0.7,0.7)
		ax.set_yticks([-0.6,-0.3,0,0.3,0.6])
		ax.set_ylabel('Correlation')
	ax2.tick_params(axis="x", pad=-3) # more negative, the xtick and labels go further upwards
	
	ax1.set_title(r'$\bf{(A)}$' + ' ' + 'Pre-industrial control simulations', loc='left', size=11, pad=30)
	ax2.set_title(r'$\bf{(B)}$' + ' ' + 'Historical simulations', loc='left', size=11, pad=30)

	plt.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=None, hspace=0.7)
	plt.savefig('./%s_%s.png' %(dt.date.today(), fname), bbox_inches='tight', dpi=300)

