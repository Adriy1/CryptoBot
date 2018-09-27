import sys
import argparse
import time
import pprint
import urllib2
import urllib

from botchart import BotChart
from botstrategy import BotStrategy
from botlog import BotLog
from botcandlestick import BotCandlestick
from plotgraphe import PlotGraphe
from stratRsi import stratRsi


def main(argv):

	# debut = '2016-11-02 14:00:00'
	# fin = '2018-08-14 20:53:20'

	try:
		parser = argparse.ArgumentParser()
		parser.add_argument("-p", "--period", help="Period length in seconds, 14400 by default", type=int, choices=[300,900,1800,7200,14400,86400],default=14400)
		parser.add_argument("-c", "--currency", help="Currency pair | Ex: USDT_ETH", default='USDT_ETH')
		parser.add_argument("-b", "--backtest", help="Mode Backtest",action="store_true")
		parser.add_argument("-s", "--start", help="Start time in YYYY-MM-DD HH:MM:SS (for backtesting), '2016-11-02 14:00:00' by default",default='2016-11-02 14:00:00')
		parser.add_argument("-e", "--end", help="End time in YYYY-MM-DD HH:MM:SS (for backtesting), '2018-12-14 20:53:20' by default",default='2018-12-14 20:53:20')
		parser.add_argument("-S", "--short", help="Enable Short Mode",action="store_true")
		args = vars(parser.parse_args())
	except:
		print "ArgumentParser Error type -h for help"
		sys.exit(2)

	pair = args["currency"]
	period = args["period"]

	short_mode = args["short"]

	if (args["backtest"]):

		debut = args['start']
		fin = args['end']

		chart = BotChart("poloniex",pair,period,debut,fin)

		strategy = stratRsi(period=period,short_mode=short_mode)

		for candlestick in chart.getPoints():
			strategy.tick(candlestick)

		graphe = PlotGraphe(chart,strategy)
		graphe.plotChart()

		try:
			sigma = chart.getSigma()*float(chart.compteur)**0.5
			perf = graphe.perf
			sharpeRatio = perf/sigma
			print("\n Perforance: "+str(perf))
			print("\n Ratio de Sharpe: "+str(sharpeRatio)+"\n")
		except Exception as e:
			pass


	else:
		chart = BotChart("poloniex",pair,period,backtest=False)

		strategy = stratRsi(period,short_mode,backtest=False)

		candlesticks = []
		developingCandlestick = BotCandlestick(period=period)

		while True:
			try:
				developingCandlestick.tick(chart.getCurrentPrice())
			except urllib2.URLError:
				time.sleep(int(30))
				developingCandlestick.tick(chart.getCurrentPrice())

			if (developingCandlestick.isClosed()):
				print("CLOSE -----")
				candlesticks.append(developingCandlestick)
				strategy.tick(developingCandlestick)
				developingCandlestick = BotCandlestick(period=period,startTime=time.time())
				print(developingCandlestick.startTime,time.time())

			time.sleep(int(30))

if __name__ == "__main__":
	main(sys.argv[1:])
