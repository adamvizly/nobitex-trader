from datetime import datetime
from ta.utils import dropna
from ta.trend import SMAIndicator, MACD
from ta.momentum import RSIIndicator
from ta.volatility import AverageTrueRange
    

class IndicatorStatus:
    sell = False
    buy = False
    latest_candle = None
    second_latest_candle = None
    
    def apply_indicator(self) -> None:
        pass

    def get_signal(self) -> tuple[bool, bool]:
        pass


class RSI(IndicatorStatus):
    def __init__(self, df, period) -> None:
        self.df = df
        self.rsi = RSIIndicator(close=df['close'], window=period)
        self.latest_candle = df.iloc[[-1]]
        self.second_latest_candle = df.iloc[[-2]]
    
    def apply_indicator(self) -> None:
        self.df['RSI'] = self.rsi.rsi()

    def get_signal(self, sell_threshold, buy_threshold) -> tuple[bool, bool]:
        self.sell = self.latest_candle['RSI'].values[0] > sell_threshold
        self.buy = self.latest_candle['RSI'].values[0] < buy_threshold
        return (self.sell, self.buy)


class SMA(IndicatorStatus):
    def __init__(self, df, short_period, long_period) -> None:
        self.df = df
        self.shortSMA = SMAIndicator(close=df['close'], window=short_period)
        self.longSMA = SMAIndicator(close=df['close'], window=long_period)
        self.latest_candle = df.iloc[[-1]]
        self.second_latest_candle = df.iloc[[-2]]
    
    def apply_indicator(self) -> None:
        self.df['shortSMA'] = self.shortSMA.sma_indicator()
        self.df['longSMA'] = self.longSMA.sma_indicator()

    def get_signal(self) -> tuple[bool, bool]:
        pass


class MACDIndex(IndicatorStatus):
    def __init__(self, df, slow_period, fast_period, signal_period) -> None:
        self.df = df
        self.macd = MACD(close=df['close'], window_slow=slow_period, window_fast=fast_period, window_sign=signal_period)
        self.latest_candle = df.iloc[[-1]]
        self.second_latest_candle = df.iloc[[-2]]
    
    def apply_indicator(self) -> None:
        self.df['MACD'] = self.macd.macd()
        self.df['MACDS'] = self.macd.macd_signal()

    def get_signal(self) -> tuple[bool, bool]:
        self.sell = self.latest_candle['MACD'].values[0] < self.latest_candle['MACDS'].values[0]
        self.buy = self.latest_candle['MACD'].values[0] > self.latest_candle['MACDS'].values[0]


class ATR(IndicatorStatus):
    def __init__(self, df, period) -> None:
        self.df = df
        self.atr = AverageTrueRange(high=df['high'], low=df['low'], close=df['close'], window=period)
        self.latest_candle = df.iloc[[-1]]
        self.second_latest_candle = df.iloc[[-2]]
    
    def apply_indicator(self) -> None:
        self.df['ATR'] = self.atr.average_true_range()

    def get_atr(self, count) -> float:
        return self.latest_candle['ATR'].values[0] * count
