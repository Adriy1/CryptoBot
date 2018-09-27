import numpy as np
from botstrategy import BotStrategy

class stratRsi(BotStrategy):
    def __init__(self,period,short_mode=False,backtest=True):
        super(stratRsi,self).__init__(short_mode,backtest)
        self.period = period

        self.zone = 0 # 0 : pas de zones, 1 : zone 1, 2 : zone 2, 3 : zone 3
        self.priceZ1 = 9999999999
        self.rsiZ1 = 100
        self.rsiZ2 = 0
        self.rsiZ3 = 100
        self.countOpen = 0

        self.zone_c = 0
        self.rsiZ2_c = 100
        self.priceZ1_c = 0
        self.rsiZ1_c = 0
        self.rsiZ3_c = 0
        self.countClose = 0

        self.distanceMin = 5
        self.memory = 1000


        self.RSI_data = []
        self.RSI_moyenne = []

    def condRsiOpen(self):
        rsi = self.indicators.RSI(self.prices,14)
        seuilmin = 30

        # if self.period <= 1800:
        #     self.RSI_data.append(rsi)
        #     self.RSI_moyenne.append(self.indicators.simpleAverage(self.RSI_data,12))
        #     rsi = self.RSI_moyenne[-1]
        #     seuilmin = 33.3

        if self.countOpen > self.memory:
            self.resetOpen()


        if self.zone == 1:
            self.rsiZ1 = min(rsi,self.rsiZ1)
            self.priceZ1 = min(self.currentPrice,self.priceZ1) # on stocke le prix minimal
            if rsi > seuilmin: #on passe en zone 2
                self.rsiZ2 = rsi
                self.zone = 2


        elif self.zone == 2:
            self.rsiZ2 = max(rsi,self.rsiZ2) # on stocke le rsi de la zone 2
            if self.currentPrice < self.priceZ1*0.98 :
                if (rsi < self.rsiZ2-(self.rsiZ1-self.rsiZ2)/2 or rsi <seuilmin) and rsi > self.rsiZ1 and self.countOpen >= self.distanceMin: # divergence : on passe en zone 3
                    self.rsiZ3 = rsi
                    self.zone = 3
                elif rsi < self.rsiZ1:
                    self.rsiZ1 = rsi
                    self.zone = 1
            if rsi > 70: # on reset si le rsi remonte trop
                self.resetOpen()


        elif self.zone == 3:
            self.rsiZ3 = min(rsi,self.rsiZ3)
            if rsi > self.rsiZ2: # achat
                self.resetOpen()
                return True
            elif self.rsiZ3 < self.rsiZ1 * 0.99:
                # self.resetOpen()
                self.rsiZ1 = rsi
                self.priceZ1 = self.currentPrice
                self.zone = 1
                self.countOpen = 0



        else:
            if rsi < seuilmin:
                self.resetOpen()
                self.zone = 1
                self.rsiZ1 = min(rsi,self.rsiZ1)


        if self.zone != 0:
            self.countOpen += 1
        return False



    def condRsiClose(self):
        rsi = self.indicators.RSI(self.prices)

        # if self.period <= 1800:
        #     self.RSI_data.append(rsi)
        #     self.RSI_moyenne.append(self.indicators.simpleAverage(self.RSI_data,12))
        #     rsi = self.RSI_moyenne[-1]
        #
        if self.countClose > self.memory:
            self.resetClose()


        if self.zone_c == 1:
            self.rsiZ1_c = max(rsi,self.rsiZ1_c)
            self.priceZ1_c = max(self.currentPrice,self.priceZ1_c) # on stocke le prix maximal
            if rsi < 70: #on passe en zone 2
                self.rsiZ2_c = rsi
                self.zone_c = 2


        elif self.zone_c == 2:
            self.rsiZ2_c = min(rsi,self.rsiZ2_c) # on stocke le rsi de la zone 2
            if self.currentPrice > self.priceZ1_c*1.02:
                # print(rsi,self.rsiZ1_c,self.rsiZ2_c,self.currentPrice)
                if (rsi > self.rsiZ1_c-(self.rsiZ1_c-self.rsiZ2_c)/2 or rsi > 70) and rsi < self.rsiZ1_c and self.countClose >= self.distanceMin:
                    self.rsiZ3_c = rsi
                    self.zone_c = 3
                elif rsi > self.rsiZ1_c:
                    self.rsiZ1_c = rsi
                    self.zone_c = 1
            if rsi < 30: # on reset si le rsi descend trop
                self.resetClose()


        elif self.zone_c == 3:
            self.rsiZ3_c = max(rsi,self.rsiZ3_c)
            # print(rsi,self.rsiZ2_c)
            if rsi < self.rsiZ2_c: #on passe en zone 4
                self.resetClose()
                return True
            elif self.rsiZ3_c > self.rsiZ1_c * 1.01:
                self.rsiZ1_c = rsi
                self.zone_c = 1
                self.countClose = 0
                self.priceZ1_c = self.currentPrice


        else:
            if rsi > 70:
                self.resetClose()
                self.zone_c = 1
                self.rsiZ1_c = max(rsi,self.rsiZ1_c)


        if self.zone_c != 0:
            self.countClose += 1
        return False



    def conditionRsi2Open(self):
        return 30 > self.indicators.RSI(self.prices)


    def conditionRsi2Close(self):
        return 70 < self.indicators.RSI(self.prices)


    def condBreakoutClose(self):
        resistance = self.indicators.saitta_support_resistance(self.high,self.low,12)[1]
        return self.currentPrice > resistance


    def resetOpen(self):
        self.countOpen = 0
        self.zone = 0
        self.rsiZ2 = 0
        self.priceZ1 = 999999
        self.rsiZ1 = 100
        self.rsiZ3 = 100

    def resetClose(self):
        self.countClose = 0
        self.zone_c = 0
        self.rsiZ2_c = 100
        self.priceZ1_c = 0
        self.rsiZ1_c = 0
        self.rsiZ3_c = 0

    def conditionOpen(self):
        if len(self.prices) > 14:
            if self.short_mode:
                return self.condRsiClose()
            else:
                return self.condRsiOpen()
        else:
            return False

    def conditionClose(self,trade):
        return False # inutile pour signaux
        # return self.condRsiClose()


    # def conditionOpen(self,candlestick):
    #     span_B = self.indicators.simpleAverage(self.prices,200)
    #     if self.prices[-1] > span_B:
    #         return self.conditionRsi2Open()
    #     # return (self.condRsiOpen() or self.conditionRsi2Open())
    #     else:
    #         return self.condRsiOpen()
    #
    # def conditionClose(self,candlestick,trade):
    #     span_B = self.indicators.simpleAverage(self.prices,200)
    #     if self.prices[-1] > span_B:
    #         return self.condRsiClose()
    #     # return (self.condRsiClose() or self.conditionRsi2Close())
    #     else:
    #         return self.conditionRsi2Close()
