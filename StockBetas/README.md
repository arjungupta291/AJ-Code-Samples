# Teza S&P500 Beta Project

This project contains modules to download 2 years of daily historical stock data for securities in the S&P500, to calculate the beta and average daily trading volume for each security, and to perform statistical analyses (with visualizations) in order to discover a relationship between average daily trading volume(X) and security beta(Y).

## Summary of Directory  Structure 

### Root Directory

Contains Python Code modules and README.

### RawFiles Directory

Contains an SnPComposition sub-directory with a csv listing all the securities currently in the S&P500 and a HistoricalStockData sub-directory with csv's for all the downloaded historical stock data on a per security basis.

### Results Directory

Contains a file called BetaResults.csv which contains the final calculation results for beta and average daily volume. It also contains a series of summaries and visualizations for the various analyses run and a written report of the results called FinalReport.pdf.

## Summary of Python Modules

### Config.py

Contains a variety of configuration information and utility methods.

### DownloadHistoricalData.py

This module can be run directly and will use the AlphaVantage API to download the source stock data. Since the API is free, there is a limitation on requests per second.This means that, even though we try to set a delay between request batches, requests fail. To combat this, we only send requests for data not already downloaded.Furthermore, when all data is downloaded, the script will make this known. Until then, the script must be run multiple times to gather all data. 

### BetaCalculator.py

The main functionality of the project lies here. The module uses pandas and numpy to load stock data into data frames and calculate betas and average daily volumes. It also uses the multiprocessing library to run batches of stocks in parallel. At the completion of all the calculations, the results are written to a csv in the Results Directory.

### ResultsAnalyzer.py

This module performs analyses consisting of linear regression, bucketing, and anova. It also renders supporting visualizations. The visualizations and analysis summaries are written to the Results directory.

### Run.py

This is the main entry point of the program once all raw data has been downloaded. If beta calculation results have already been computed and saved in the BetaResults.csv file, then that file is used to build a dataframe with which to run the ResultsAnalyzer module. If no such file exists, then the BetaCalculator module is run to compute/aggregate the results and then the subsequent analyses are performed and saved.

## Final Report

The FinalReport.pdf is a written summary of the findings and will be found in the Results directory.