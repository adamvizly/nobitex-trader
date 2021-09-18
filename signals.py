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

    def get_signal(self) -> tuple[bool, bool]:
        self.sell = self.latest_candle['RSI'].values[0] > 70
        self.buy = self.latest_candle['RSI'].values[0] < 30
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
        pass


class ATR(IndicatorStatus):
    def __init__(self, df, period) -> None:
        self.df = df
        self.atr = AverageTrueRange(high=df['high'], low=df['low'], close=df['close'], window=period)
        self.latest_candle = df.iloc[[-1]]
        self.second_latest_candle = df.iloc[[-2]]
    
    def apply_indicator(self) -> None:
        self.df['ATR'] = self.atr.average_true_range()

    def get_signal(self) -> tuple[bool, bool]:
        pass


def get_signal(df):
    df = dropna(df)
    df = RSI(df, 14)
    df = MACDIndex(df, 26, 12, 9)
    latest_data = df.tail(1)
    second_latest_data = df.iloc[-2:-1]
    macd_sell = (latest_data['MACD'].values[0] < latest_data['MACDS'].values[0]) and (second_latest_data['MACD'].values[0] >= second_latest_data['MACDS'].values[0]) 
    macd_buy = (latest_data['MACD'].values[0] > latest_data['MACDS'].values[0]) and (second_latest_data['MACD'].values[0] <= second_latest_data['MACDS'].values[0]) 
    rsi_sell = (latest_data['RSI'].values[0] > 70) and (second_latest_data['RSI'].values[0] <= 70)
    rsi_buy = (latest_data['RSI'].values[0] < 30) and (second_latest_data['RSI'].values[0] >= 30)
    return {'buy': macd_buy and rsi_buy, 'sell': macd_sell and rsi_sell, 'time': datetime.fromtimestamp(latest_data['time'])}


def back_test_signal(df):
    df = dropna(df)
    df = RSI(df, 14)
    df = MACDIndex(df, 26, 12, 9)
    df = ATR(df, 14)
    buy_price = 0
    profit = 0
    step_loss = 0
    for index, row in df.iterrows():
        if index <= 14:
            continue
        latest_data = df.iloc[[index]]
        second_latest_data = df.iloc[[index - 1]]
        macd_sell = (latest_data['MACD'].values[0] < latest_data['MACDS'].values[0]) and (second_latest_data['MACD'].values[0] >= second_latest_data['MACDS'].values[0]) 
        macd_buy = (latest_data['MACD'].values[0] > latest_data['MACDS'].values[0]) and (second_latest_data['MACD'].values[0] <= second_latest_data['MACDS'].values[0]) 
        rsi_sell = (latest_data['RSI'].values[0] > 70) and (second_latest_data['RSI'].values[0] <= 70)
        rsi_buy = (latest_data['RSI'].values[0] < 30) and (second_latest_data['RSI'].values[0] >= 30)
        buy = macd_buy
        sell = macd_sell
        price = latest_data['close'].values[0]
        atr = latest_data['ATR'].values[0]
        ttt = datetime.fromtimestamp(latest_data['time'])
        if step_loss > 0 and buy_price > 0 and price <= step_loss:
            profit += price - buy_price
            print(f'selling at price {price}, you made {profit} at time {ttt}')
            step_loss = 0
        if buy:
            buy_price = price
            print(f'buying at price {price} at time {ttt}')
            step_loss = price - atr
        if sell and buy_price > 0:
            profit += price - buy_price
            print(f'selling at price {price}, you made {profit} at time {ttt}')
        # print({'buy': {'RSI': rsi_buy, 'MACD': macd_buy}, 'sell': {'RSI': rsi_sell, 'MACD': macd_sell}, 'time': datetime.fromtimestamp(latest_data['time'])})

