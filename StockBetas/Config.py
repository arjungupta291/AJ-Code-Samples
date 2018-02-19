FILE_STORAGE_CONFIG = {
	"SnPSecuritiesCompositionFile" : "RawFiles/SnPComposition/snp_securities.csv",
	"HistoricalStockDataDirectory" : "RawFiles/HistoricalStockData/",
	"CompressedHistoricalDataFile" : "RawFiles/HistoricalStockData/all_data.csv",
	"ResultsFile" : "Results/Results.csv"
}

ALPHAVANTAGE_API_CONFIG = {
	"ApiKey" : "FA6DKLC8999DSURX",
	"BaseUrl" : "https://www.alphavantage.co/query?",
	"QueryString" : "function={0}&symbol={1}&apikey={2}&datatype={3}&outputsize={4}",
	"Function" : "TIME_SERIES_DAILY",
	"DataFormat" : "csv",
	"OutputSize" : "full"
}

STOCK_DATA_CONFIG = {
	"BenchmarkTicker_SPY" : 'SPY',
	"NumberOfHistoricalDailyDataPoints" : 600,
	"DataColumns" : ['ticker', 'timestamp', 'open', 'high', 'low', 'close', 'volume'],
	"NumericalColumns" : ['open', 'high', 'low', 'close', 'volume'],
	"ReturnsPeriod" : 1,
	"ResultsColumns" : ["ticker", "beta", "avgVolume"]
}

def getFullSnPTickerList():
	fname = FILE_STORAGE_CONFIG["SnPSecuritiesCompositionFile"]
	ticker_index = 0
	with open(fname, 'r+') as f:
		split_lines = [l.split(',') for l in f.readlines()]
		return [s[ticker_index] for s in split_lines]

def getNumberOfSecurities():
	return len(getFullSnPTickerList())

def buildApiRequest(ticker):
	return (ALPHAVANTAGE_API_CONFIG["BaseUrl"] +
	        ALPHAVANTAGE_API_CONFIG["QueryString"].format(
	        ALPHAVANTAGE_API_CONFIG["Function"], ticker,
	        ALPHAVANTAGE_API_CONFIG["ApiKey"],
	        ALPHAVANTAGE_API_CONFIG["DataFormat"],
	        ALPHAVANTAGE_API_CONFIG["OutputSize"]))

def getHistoricalDataFilename(ticker):
	return (FILE_STORAGE_CONFIG["HistoricalStockDataDirectory"] +
		    ticker + ".csv")