from timeit import default_timer as timer
import pandas as pd
import numpy as np
from multiprocessing import Pool, cpu_count
from functools import partial
import Config

def runBetaCalculator():
	p = Pool(cpu_count())
	allTickers = Config.getSnPTickerListForAnalysis()
	print("Running Beta Calculator for: " + str(len(allTickers)) + " Securities")
	print("Retreiving Benchmark Data")
	benchmarkTicker = Config.STOCK_DATA_CONFIG["BenchmarkTicker_SPY"]
	spy_returns, spy_avg_daily_vol = getHistoricalStockMetrics(benchmarkTicker)
	print("Running Individual Stock Calculations")
	start = timer()
	results = p.map(partial(buildStockResult, spy_returns=spy_returns), allTickers)
	end = timer()
	print("All Betas Calculated. Time Taken: " + str(end - start))
	p.close()
	p.join()
	print("Building Results DataFrame")
	df_results = buildResultsDataFrame(results)
	print("Writing to Results File")
	writeToResultsFile(df_results)
	return df_results

def buildStockResult(ticker, spy_returns):
	try:
		stock_returns, avg_daily_vol = getHistoricalStockMetrics(ticker)
		beta = calculateStockBeta(stock_returns, spy_returns)
		return np.array([ticker, beta, avg_daily_vol])
	except:
		return np.array([ticker, np.NaN, np.NaN])

def calculateStockBeta(stock_returns, spy_returns):
	stock_returns_available = len(stock_returns)
	X = np.stack((stock_returns.values[1:],  spy_returns.values[1:stock_returns_available]), axis=0)
	covariance_matrix = np.cov(X)
	beta = covariance_matrix[0][1] / covariance_matrix[1][1]
	return beta

def getHistoricalStockMetrics(ticker):
	df_stock = buildStockDataframe(ticker)
	returns_period = Config.STOCK_DATA_CONFIG["ReturnsPeriod"]
	stock_returns = df_stock["close"].pct_change(returns_period)
	average_daily_volume = df_stock["volume"].mean()
	return stock_returns, average_daily_volume

def buildStockDataframe(ticker):
	fname = Config.getHistoricalDataFilename(ticker)
	columnNames = Config.STOCK_DATA_CONFIG["DataColumns"]
	with open(fname, 'r+') as f:
		lines = [l.strip('\n\r').split(',') for l in f.readlines()[1:]]
		df = pd.DataFrame(index=np.arange(0, len(lines)), columns=columnNames)
		for r in range(len(lines)):
			df.loc[r] = [ticker] + lines[r]
	numericalColumns = Config.STOCK_DATA_CONFIG["NumericalColumns"]
	configureNumericalColumns(df, numericalColumns)
	return df

def buildResultsDataFrame(calculator_results):
	results_columns = Config.STOCK_DATA_CONFIG["ResultsColumns"]
	df = pd.DataFrame(index=np.arange(0, len(calculator_results)), columns=results_columns)
	for r in range(len(calculator_results)):
		df.loc[r] = calculator_results[r]
	configureNumericalColumns(df, ["beta", "avgVolume"])
	return df

def configureNumericalColumns(df, columns):
	df[columns] = df[columns].apply(pd.to_numeric)

def writeToResultsFile(df_results):
	results_file = Config.FILE_STORAGE_CONFIG["ResultsFile"]
	df_results.to_csv(results_file)


