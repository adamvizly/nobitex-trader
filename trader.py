from datetime import datetime, timedelta
from time import sleep
from nobitex import Nobitex
from strategy import BBandRSI

market = 'XLMIRT'
nt = Nobitex()
df = nt.get_ohlc(market, '60', datetime.now() - timedelta(days=30), datetime.now())

print('new loop')
bb_rsi_strat = BBandRSI(df, 30, 2, 13)
bb_rsi_strat.apply_indicator()
test = bb_rsi_strat.back_test(10*24)
for item in test:
    print(item)
    # bb_rsi_strat = BBandRSI(df, 30, 2, 13)
    # bb_rsi_strat.apply_indicator()
    # print(datetime.now(), bb_rsi_strat.action())
