from BetaCalculator import runBetaCalculator
from ResultsAnalyzer import runFullAnalysis
import pandas as pd
import Config

def run():
	if Config.resultsAlreadyComputed():
		print("Results File Already Exists")
		results_file = Config.FILE_STORAGE_CONFIG["ResultsFile"]
		df_results = pd.read_csv(results_file)
	else:
		df_results = runBetaCalculator()
	runFullAnalysis(df_results)


if __name__ == '__main__':
	run()