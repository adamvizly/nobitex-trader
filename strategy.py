from datetime import datetime
from ta.trend import MACD
from ta.momentum import RSIIndicator
from ta.volatility import AverageTrueRange, BollingerBands
    

class Strategy:
    df = None
    latest_candle = None
    second_latest_candle = None
    stop_loss = None
    take_profit = None
    
    def apply_indicator(self) -> None:
        pass
    
    def action(self) -> str:
        pass

    def back_test(self, candles_before) -> list:
        pass


class RSI(Strategy):
    def __init__(self, df, period) -> None:
        self.df = df
        self.rsi = RSIIndicator(close=df['close'], window=period)
    
    def apply_indicator(self) -> None:
        self.df['RSI'] = self.rsi.rsi()
        self.latest_candle = self.df.iloc[-1]
        self.second_latest_candle = self.df.iloc[-2]
    
    def action(self, upperbound, lowerbound) -> str:
        if self.latest_candle['RSI'] > upperbound:
            return 'sell'
        elif self.latest_candle['RSI'] < lowerbound:
            return 'buy'
    
    def back_test(self, candles_before, upperbound, lowerbound) -> list:
        test_df = self.df.iloc[-candles_before:]
        actions = []
        for index, row in test_df.iterrows():
            if row['RSI'] > upperbound:
                actions.append((datetime.fromtimestamp(row['time']).strftime('%Y-%m-%d %H:%M:%S'), row['RSI'], 'sell'))
            elif row['RSI'] < lowerbound:
                actions.append((datetime.fromtimestamp(row['time']).strftime('%Y-%m-%d %H:%M:%S'), row['RSI'], 'buy'))
            else:
                actions.append((datetime.fromtimestamp(row['time']).strftime('%Y-%m-%d %H:%M:%S'), row['RSI'], 'hold'))
        return actions


class MACDIndex(Strategy):
    def __init__(self, df, slow_period, fast_period, signal_period) -> None:
        self.df = df
        self.macd = MACD(close=df['close'], window_slow=slow_period, window_fast=fast_period, window_sign=signal_period)
    
    def apply_indicator(self) -> None:
        self.df['MACD'] = self.macd.macd()
        self.df['MACDS'] = self.macd.macd_signal()
        self.latest_candle = self.df.iloc[-1]
        self.second_latest_candle = self.df.iloc[-2]
    
    def action(self) -> str:
        if self.latest_candle['MACD'] > self.latest_candle['MACDS']:
            return 'buy'
        elif self.latest_candle['MACD'] < self.latest_candle['MACDS']:
            return 'sell'

    def back_test(self, candles_before) -> list:
        test_df = self.df.iloc[-candles_before:]
        actions = []
        for index, row in test_df.iterrows():
            if row['MACD'] < row['MACDS']:
                actions.append((datetime.fromtimestamp(row['time']).strftime('%Y-%m-%d %H:%M:%S'), row['MACD'], row['MACDS'], 'sell'))
            elif row['MACD'] > row['MACDS']:
                actions.append((datetime.fromtimestamp(row['time']).strftime('%Y-%m-%d %H:%M:%S'), row['MACD'], row['MACDS'], 'buy'))
            else:
                actions.append((datetime.fromtimestamp(row['time']).strftime('%Y-%m-%d %H:%M:%S'), row['MACD'], row['MACDS'], 'hold'))
        return actions

class ATR(Strategy):
    def __init__(self, df, period) -> None:
        self.df = df
        self.atr = AverageTrueRange(high=df['high'], low=df['low'], close=df['close'], window=period)
    
    def apply_indicator(self) -> None:
        self.df['ATR'] = self.atr.average_true_range()
        self.latest_candle = self.df.iloc[-1]
        self.second_latest_candle = self.df.iloc[-2]

    def get_atr(self, count) -> float:
        return self.latest_candle['ATR'] * count


class BollingerBand(Strategy):
    def __init__(self, df, period, dev_period) -> None:
        self.df = df
        self.bb = BollingerBands(close=df['close'], window=period, window_dev=dev_period)
    
    def apply_indicator(self) -> None:
        self.df['BBH'] = self.bb.bollinger_hband()
        self.df['BBL'] = self.bb.bollinger_lband()
        self.df['BBHI'] = self.bb.bollinger_hband_indicator()
        self.df['BBLI'] = self.bb.bollinger_lband_indicator()
        self.latest_candle = self.df.iloc[-1]
        self.second_latest_candle = self.df.iloc[-2]

    def action(self) -> str:
        if self.latest_candle['BBHI']:
            return 'sell'
        elif self.latest_candle['BBLI']:
            return 'buy'
    
    def back_test(self, candles_before) -> list:
        test_df = self.df.iloc[-candles_before:]
        actions = []
        for index, row in test_df.iterrows():
            if row['BBHI']:
                actions.append((datetime.fromtimestamp(row['time']).strftime('%Y-%m-%d %H:%M:%S'), row['BBHI'], 'sell'))
            elif row['BBLI']:
                actions.append((datetime.fromtimestamp(row['time']).strftime('%Y-%m-%d %H:%M:%S'), row['BBLI'], 'buy'))
            else:
                actions.append((datetime.fromtimestamp(row['time']).strftime('%Y-%m-%d %H:%M:%S'), 'hold'))
        return actions


class BBandRSI(Strategy):
    def __init__(self, df, bb_period, bb_dev_period, rsi_period) -> None:
        self.df = df
        self.rsi = RSI(df, period=rsi_period)
        self.bb = BollingerBand(df, period=bb_period, dev_period=bb_dev_period)
    
    def apply_indicator(self) -> None:
        self.rsi.apply_indicator()
        self.bb.apply_indicator()
    
    def action(self) -> str:
        if self.rsi.action(upperbound=75, lowerbound=25) == 'sell' and self.bb.action() == 'sell':
            return 'sell'
        elif self.rsi.action(upperbound=75, lowerbound=25) == 'buy' and self.bb.action() == 'buy':
            return 'buy'
        return 'hold'
    
    def back_test(self, candles_before) -> list:
        actions = []
        rsi_tests = self.rsi.back_test(candles_before, upperbound=75, lowerbound=25)
        bb_tests = self.bb.back_test(candles_before)
        for rsi_test in rsi_tests:
            for bb_test in bb_tests:
                if rsi_test[0] == bb_test[0]:
                    if rsi_test[-1] == bb_test[-1] == 'sell':
                        actions.append((rsi_test[0], 'sell'))
                    elif rsi_test[-1] == bb_test[-1] == 'buy':
                        actions.append((rsi_test[0], 'buy'))
                    else:
                        actions.append((rsi_test[0], 'hold'))
        return actions
