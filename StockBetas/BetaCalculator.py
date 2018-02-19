import time
import pandas as pd
import numpy as np
from multiprocessing import Pool, cpu_count
from functools import partial
import Config

def calc(ticker, spy_returns, spy_std):
	try:
		stock_returns, stock_std, avg_daily_vol = getHistoricalStockMetrics(ticker)
		beta = calculateStockBeta(stock_returns, spy_returns, stock_std, spy_std)
		return [(ticker, beta, avg_daily_vol)]
	except:
		return [(ticker, np.NaN, np.NaN)]

def calculateStockBeta(stock_returns, spy_returns, stock_std, spy_std):
	correlation = stock_returns.corrwith(spy_returns).values[0]
	beta = correlation * (stock_std / spy_std)
	return beta

def getHistoricalStockMetrics(ticker):
	numberOfRows = Config.STOCK_DATA_CONFIG["NumberOfHistoricalDailyDataPoints"]
	columnNames = Config.STOCK_DATA_CONFIG["DataColumns"]
	df_stock = pd.DataFrame(index=np.arange(0, numberOfRows), columns=columnNames)
	populateDataframe(ticker, df_stock)
	stock_close_prices = df_stock.iloc[:,5:6]
	stock_returns = stock_close_prices.pct_change(1)
	stock_std = stock_returns.std().values[0]
	average_daily_volume = df_stock["volume"].mean()
	return stock_returns, stock_std, average_daily_volume

def populateDataframe(ticker, df):
	fname = Config.getHistoricalDataFilename(ticker)
	with open(fname, 'r+') as f:
		split_lines = [l.strip('\n\r').split(',') for l in f.readlines()[1:]]
		for r in range(len(split_lines)):
			df.iloc[r] = [ticker] + split_lines[r]
	configureNumericalColumns(df)

def configureNumericalColumns(df):
	numericalColumns = Config.STOCK_DATA_CONFIG["NumericalColumns"]
	df[numericalColumns] = df[numericalColumns].apply(pd.to_numeric)


if __name__ == '__main__':
	p = Pool(cpu_count() + 1)
	allTickers = Config.getFullSnPTickerList()
	benchmarkTicker = Config.STOCK_DATA_CONFIG["BenchmarkTicker_SPY"]
	spy_returns, spy_std, spy_avg_daily_vol = getHistoricalStockMetrics(benchmarkTicker)
	time_start = time.time()
	results = p.map(partial(calc, spy_returns=spy_returns, spy_std=spy_std), allTickers)
	p.close()
	p.join()
	time_end = time.time()
	print("All Betas Calculated. Time Taken: " + str(time_end - time_start))
	for r in results:
		print(r)

