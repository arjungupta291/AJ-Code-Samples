import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.api as sm
import seaborn as sns
import scipy.stats as stats
import Config

def runFullAnalysis(df_results):
	print("Running Complete Analysis")
	runLinearRegression(df_results)
	performBucketingTransforms(df_results, 10)
	computeBucketingSummary(df_results)
	saveBucketingVisualizations(df_results)
	runAnova(df_results)
	saveScatterPlot(df_results)
	print("All Analysis Components Saved to Results Directory")

def runLinearRegression(df):
	model = sm.OLS(df["beta"], df["avgVolume"])
	result = model.fit()
	saveToTextfile("regressionSummary.txt", str(result.summary()))

def runAnova(df):
	groups = []
	for i in df['bins'].unique():
		group = []
		group.append(list(df.loc[df['bins'] == i]['beta']))
		groups.extend(group)
	results = stats.f_oneway(*groups)
	saveToTextfile("anovaResults.txt", str(results))

def performBucketingTransforms(df, number):
	new_col = "avgVolume" + '_' + 'cat'
	df[new_col] = pd.qcut(df["avgVolume"], number)
	df["bins"] = pd.qcut(df["avgVolume"], number, labels = range(1, number+1))

def computeBucketingSummary(df):
	med = df.groupby(['bins', 'avgVolume_cat'])['beta'].median()
	avg = df.groupby(['bins', 'avgVolume_cat'])['beta'].mean()
	result = pd.concat([avg, med],axis = 1, join = 'inner')
	result.columns = ['Mean', 'Median']
	result.index.names = ['Group', 'Cutoffs']
	saveToTextfile("bucketingSummary.txt", str(result))

def saveScatterPlot(df):
	plt.scatter(df['avgVolume'], df['beta'])
	savePlot(plt, "scatter.png")

def saveBucketingVisualizations(df):
	f, ax = plt.subplots(1, 2, figsize = (20,8))
	sns.boxplot('bins', 'beta', data = df, ax = ax[0])
	ax[0].set_title('Beta Boxplots by Group')
	g = sns.factorplot('bins', 'beta', data = df, ax = ax[1])
	ax[1].set_title('Beta Means by Group')
	plt.close(g.fig)
	savePlot(plt, "bucketingPlots.png")

def saveToTextfile(filename, text):
	directory = Config.FILE_STORAGE_CONFIG["ResultsDirectory"]
	with open(directory + filename, "w") as f:
		f.write(text)

def savePlot(plt, filename):
	directory = Config.FILE_STORAGE_CONFIG["ResultsDirectory"]
	plt.savefig(directory + filename)

