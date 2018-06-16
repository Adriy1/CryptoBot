import numpy
from expAverage import expAverage
from pointPivot import pointPivot

class BotIndicators(object):
	def __init__(self):
		self.exp_Average = 0
		pass

	def momentum(self, dataPoints, period=14):
		if (len(dataPoints) > period -1):
			return dataPoints[-1] * 100 / dataPoints[-period]

	def EMA(self, prices, period):
		x = numpy.asarray(prices)
		weights = None
		weights = numpy.exp(numpy.linspace(-1., 0., period))
		weights /= weights.sum()

		a = numpy.convolve(x, weights, mode='full')[:len(x)]
		a[:period] = a[period]
		return a

	def MACD(self, prices, nslow=26, nfast=12):
		emaslow = self.EMA(prices, nslow)
		emafast = self.EMA(prices, nfast)
		return emaslow, emafast, emafast - emaslow

	def RSI(self, prices, period=14):
		deltas = numpy.diff(prices)
		seed = deltas[:period+1]
		up = seed[seed >= 0].sum()/period
		down = -seed[seed < 0].sum()/period
		if down != 0:
			rs = up/down
		else:
			rs = 1
		rsi = numpy.zeros_like(prices)
		rsi[:period] = 100. - 100./(1. + rs)
		for i in range(period, len(prices)):
 			delta = deltas[i - 1]  # cause the diff is 1 shorter
  			if delta > 0:
 				upval = delta
 				downval = 0.
 			else:
 				upval = 0.
 				downval = -delta

 			up = (up*(period - 1) + upval)/period
 			down = (down*(period - 1) + downval)/period
  			rs = up/down
 			rsi[i] = 100. - 100./(1. + rs)
  		if len(prices) > period:
 			return rsi[-1]
 		else:
 			return 50 # output a neutral amount until enough prices in list to calculate RSI

	def expAverage(self,prices,candlestick,nbPeriod):
		if self.exp_Average != 0:
			self.exp_Average = (2/float(nbPeriod+1))*candlestick.close+(1-2/float(nbPeriod+1))*self.exp_Average
		else:
			self.exp_Average = candlestick.close
		return self.exp_Average

	def simpleAverage(self,prices,nbPeriod):
	 	return sum(prices[-nbPeriod:]) / float(len(prices[-nbPeriod:]))

	def pointPivot(self,candlestick):
		return (candlestick.high + candlestick.low + candlestick.close)/float(3)

	def stochastique(self,prices,low,high,nbPeriod=14):
		if (len(low)>nbPeriod):
			return 100*(prices[-1]-min(low[-nbPeriod:]))/(max(high[-nbPeriod:])-min(low[-nbPeriod:]))
		else:
			return -1
