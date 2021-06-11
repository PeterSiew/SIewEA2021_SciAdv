import numpy as np
import matplotlib.pyplot as plt
import matplotlib

def leadlag_grid_plotting(rows, xlabels, boxplots=None, bpcolors=None, lines=None, linescolors=None, left_titles=None, top_titles=None, pltf=None, ax_all=None, sig_line=True, ylims=None, yticks=None,noborder=True, legend_element=None, out_whis=None, dots=None, fig_xsize=6, fn_add='', showfliers=True, xadjust=None, xadjust_line=None, widths=None, bp_show_median=True, zorder=None,real_boxplot=True,eb_marker='s',evl_width=None, eb_full=False):

	# All of them have a share x
	x = np.arange(len(xlabels))
	#sig_corr = 2.026 / (37+2.026**2)**0.5 # Samples size of 39 (df=37)
	sig_corr = 2.024 / (38+2.024**2)**0.5 #Sample size of 40 (df=38)
	plt.close() if pltf is None else ''
	fig = plt.figure(figsize=(fig_xsize, rows*2.5)) if pltf is None else pltf
	for i in range(rows):
		ax = fig.add_subplot(rows, 1, i+1) if ax_all is None else ax_all[i]
		if not boxplots is None:
			len_models = len(boxplots[i])
			xadjust_width = len_models * 0.05
			xadjust = np.linspace(-xadjust_width, xadjust_width, len_models) if xadjust is None else xadjust
			widths = [0.10] * len_models if widths is None else widths
			evl_width = [2] * len_models if evl_width is None else evl_width
			zorder = [1] * len_models if zorder is None else zorder
			for j, m in enumerate(boxplots[i]):

				#evl_width = evl_width[j] if not evl_width is None else 2
				if real_boxplot:
					#the boxplots
					bp = ax.boxplot(boxplots[i][m], positions=x+xadjust[j], widths=widths[j], patch_artist=True, whis=out_whis[i], showfliers=showfliers)
					for element in ['boxes', 'whiskers', 'caps']:
						plt.setp(bp[element], color=bpcolors[i][m], lw=2.5) # lw=3 in Fig.1
					#for cap in bp['caps']: # Make the wiskers horizonally longer
					#	cap.set(xdata=cap.get_xdata() + (-0.02,+0.02), linewidth=4.0)
					for box in bp['boxes']:
						box.set(facecolor = bpcolors[i][m])
					if bp_show_median:
						plt.setp(bp['medians'], color='white', lw=2)
					else:
						plt.setp(bp['medians'], color='None', lw=1.5)
					plt.setp(bp['fliers'], marker='o', markersize=0.2, markerfacecolor=bpcolors[i][m], markeredgecolor=bpcolors[i][m])
				else: # Alternativate boxplots (errorbars)
					# Plot the median
					medians = [np.median(boxplots[i][m][k]) for k in range(len(boxplots[i][m]))]
					if eb_full[m]:
						ymaxs = [np.max(boxplots[i][m][k]) for k in range(len(boxplots[i][m]))]
						ymins = [np.min(boxplots[i][m][k]) for k in range(len(boxplots[i][m]))]
					else:
						ymaxs = medians
						ymins = medians
					yerr_low = np.array(medians)-np.array(ymins)
					yerr_high = np.array(ymaxs)-np.array(medians)
					ax.errorbar(x+xadjust[j],medians,yerr=[yerr_low, yerr_high],fmt='o',color=bpcolors[i][m],marker=eb_marker[j],elinewidth=evl_width[j],zorder=zorder[j])

		# The long-term correlations within the boxplotsa. Now it is represented by horizonal thin black lines instead of dots
		if not dots is None: 
			if not dots[i] is None:
				for j, m in enumerate(dots[i]):
					ax.plot(x+xadjust[j], dots[i][m], marker='_', linestyle='None', markersize=8, zorder=3, markeredgecolor='k')
					#ax.plot(x+xadjust[j], dots[i][m], marker='_', linestyle='None', markersize=5, zorder=1, markeredgecolor='k')

		if not lines is None: # Showing the observations
			# This is now replaced by dots
			xadjust_line=0 if xadjust_line is None else xadjust_line
			ax.plot(x+xadjust_line, lines[i], marker='o', linestyle='None', zorder=2, color=linescolors[i])

		if sig_line==True: # Plot the sigificant line of pearson correlation with sample size of 39 (df is 37)
			ax.axhline(y=-sig_corr, xmin=0.02, xmax=0.98, color='gray', ls='--', lw=0.2)
			ax.axhline(y=sig_corr, xmin=0.02, xmax=0.98, color='gray', ls='--', lw=0.2)
			ax.axhline(y=0, xmin=0.01, xmax=0.98, color='gray', ls='--', lw=0.8)

		if not left_titles is None:
			ax.set_ylabel(left_titles[i])
		if not ylims is None:
			ax.set_ylim(ylims[0], ylims[-1])
		if not yticks is None:
			ax.set_yticks(yticks)
		if not top_titles is None:
			ax.set_title(top_titles[i], loc='left', size=10)
		if noborder:
			ax.spines['right'].set_visible(False)
			ax.spines['top'].set_visible(False)
			ax.spines['left'].set_visible(False)
			ax.spines['bottom'].set_visible(False)
			ax.tick_params(axis='x', which='both',length=0)
			ax.tick_params(axis='y', which='both',length=2)
		if not legend_element is None:
			legend = ax.legend(handles=legend_element[i], bbox_to_anchor=(1, 1), loc='upper left')
			legend.get_frame().set_linewidth(0.0)

		ax.set_xticks(x) if i==rows-1 else ax.set_xticks([])
		ax.set_xticklabels(xlabels) if i==rows-1 else ax.set_xticklabels([])

	if pltf is None:
		plt.savefig('../graphs/%s_correlation_leadlag%s.png' %(dt.date.today(), fn_add), bbox_inches='tight')
