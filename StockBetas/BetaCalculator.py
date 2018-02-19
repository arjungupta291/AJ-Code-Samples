import time
import pandas as pd
import numpy as np
import Config

def calculateStockBeta(stock_returns, spy_returns, stock_std, spy_std):
	correlation = stock_returns.corrwith(spy_returns).values[0]
	beta = correlation * (stock_std / spy_std)
	return beta

def getBenchmarkSPYData():
	etfTicker = 'SPY'
	numberOfRows = Config.STOCK_DATA_CONFIG["NumberOfHistoricalDailyDataPoints"]
	columnNames = Config.STOCK_DATA_CONFIG["DataColumns"]
	df_spy = pd.DataFrame(index=np.arange(0, numberOfRows), columns=columnNames)
	populateDataframe(etfTicker, df_spy)
	spy_close_prices = df_spy.iloc[:,5:6]
	spy_returns = spy_close_prices.pct_change(1)
	spy_std = spy_returns.std().values[0]
	return spy_returns, spy_std

def getStockData(ticker):
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
	allTickers = Config.getFullSnPTickerList()
	spy_returns, spy_std = getBenchmarkSPYData()
	time_start = time.time()
	for t in allTickers[:30]:
		try:
			stock_returns, stock_std, avg_daily_vol = getStockData(t)
			beta = calculateStockBeta(stock_returns, spy_returns, stock_std, spy_std)
			print(t + "  " + str(round(beta, 3)) + "  " + str(round(avg_daily_vol, 0)))
		except:
			print(t + "  Calculation Failed")
	time_end = time.time()
	print("All Betas Calculated. Time Take: " + str(time_end - time_start))

