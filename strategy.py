from datetime import datetime
from ta.utils import dropna
from ta.trend import SMAIndicator, MACD
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


class RSI(Strategy):
    def __init__(self, df, period) -> None:
        self.df = df
        self.rsi = RSIIndicator(close=df['close'], window=period)
    
    def apply_indicator(self) -> None:
        self.df['RSI'] = self.rsi.rsi()
        self.latest_candle = self.df.iloc[[-1]]
        self.second_latest_candle = self.df.iloc[[-2]]
    
    def action(self, upperbound, lowerbound) -> str:
        if self.latest_candle['RSI'].values[0] > upperbound:
            return 'sell'
        elif self.latest_candle['RSI'].values[0] < lowerbound:
            return 'buy'


class MACDIndex(Strategy):
    def __init__(self, df, slow_period, fast_period, signal_period) -> None:
        self.df = df
        self.macd = MACD(close=df['close'], window_slow=slow_period, window_fast=fast_period, window_sign=signal_period)
    
    def apply_indicator(self) -> None:
        self.df['MACD'] = self.macd.macd()
        self.df['MACDS'] = self.macd.macd_signal()
        self.latest_candle = self.df.iloc[[-1]]
        self.second_latest_candle = self.df.iloc[[-2]]
    
    def action(self) -> str:
        if self.latest_candle['MACD'] > self.latest_candle['MACDS']:
            return 'buy'
        elif self.latest_candle['MACD'] < self.latest_candle['MACDS']:
            return 'sell'


class ATR(Strategy):
    def __init__(self, df, period) -> None:
        self.df = df
        self.atr = AverageTrueRange(high=df['high'], low=df['low'], close=df['close'], window=period)
    
    def apply_indicator(self) -> None:
        self.df['ATR'] = self.atr.average_true_range()
        self.latest_candle = self.df.iloc[[-1]]
        self.second_latest_candle = self.df.iloc[[-2]]

    def get_atr(self, count) -> float:
        return self.latest_candle['ATR'].values[0] * count


class BollingerBand(Strategy):
    def __init__(self, df, period, dev_period) -> None:
        self.df = df
        self.bb = BollingerBands(close=df['close'], window=period, window_dev=dev_period)
    
    def apply_indicator(self) -> None:
        self.df['BBH'] = self.bb.bollinger_hband()
        self.df['BBL'] = self.bb.bollinger_lband()
        self.df['BBHI'] = self.bb.bollinger_hband_indicator()
        self.df['BBLI'] = self.bb.bollinger_lband_indicator()
        self.latest_candle = self.df.iloc[[-1]]
        self.second_latest_candle = self.df.iloc[[-2]]

    def action(self) -> str:
        if self.latest_candle['BBHI'].values[0]:
            return 'sell'
        elif self.latest_candle['BBLI'].values[0]:
            return 'buy'


class BBandRSI(Strategy):
    pass
