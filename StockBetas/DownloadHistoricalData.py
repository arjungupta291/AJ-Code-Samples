import grequests
import csv
import time
import Config

def downloadHistoricalStockData(tickers):
	urls = [Config.buildApiRequest(t) for t in tickers]
	requests = (grequests.get(u, stream=True) for u in urls)
	responses = grequests.map(requests)

	succeeded = []
	failed = []

	for t,r in zip(tickers, responses):
		if r.status_code == 200 and 'content-disposition' in r.headers:
			fname = Config.getHistoricalDataFilename(t)
			with open(fname, 'w', newline = '') as f:
				writer = csv.writer(f)
				reader = csv.reader(r.text.splitlines())

				points = 0
				for row in reader:
					if points <= Config.STOCK_DATA_CONFIG["NumberOfHistoricalDailyDataPoints"]:
						writer.writerow(row)
						points += 1
					else:
						break
			succeeded.append(t)
		else:
			failed.append(t)

		r.close()

	return succeeded, failed

def getSnPTickerListForDownload():
	return [t for t in Config.getFullSnPTickerList() if not Config.tickerDataExists(t)]

def batch(iterable, chunk = 1):
    total_length = len(iterable)
    for ndx in range(0, total_length, chunk):
        yield iterable[ndx:min(ndx + chunk, total_length)]

if __name__ == '__main__':
	print("Retrieving S&P 500 Ticker Composition")
	tickers = getSnPTickerListForDownload()
	if tickers == []:
		print("All Data Has Been Downloaded")
	else:
		print("Starting AlphaVantage Batch Historical Stock Data Download")
		print("Retrieving Data for " + str(len(tickers)) + " Securities")
		total_async_time_start = time.time()
		batch_size = Config.ALPHAVANTAGE_API_CONFIG["BatchSize"]
		for chunk in batch(tickers, batch_size):
			print("Starting Batch: " + str(chunk))
			succeded, failed = downloadHistoricalStockData(chunk)
			print("Succeeed: " + str(len(succeded)), "Failed: " + str(failed))
			if failed:
				time.sleep(2)
		total_async_time_end = time.time()
		print("All Requests Complete. Total Time: " + str(total_async_time_end - total_async_time_start))

