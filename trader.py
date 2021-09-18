from datetime import datetime, timedelta
from time import sleep
from nobitex import Nobitex
from signals import get_signal, back_test_signal

market = 'XLMIRT'
nt = Nobitex()
df = nt.get_ohlc(market, '60', datetime.now() - timedelta(days=30), datetime.now())
while True:
    print('new loop')
    back_test_signal(df)
    # if datetime.now().minute == 1:
    #     df = nt.get_ohlc(market, '60', datetime.now() - timedelta(days=2), datetime.now())
    # signal = get_signal(df)
    # print(signal)
    # if signal['buy']:
    #     print('auto buying')
    # elif signal['sell']:
    #     print('auto selling')
    # else:
    #     print('not sure what to do, holding')

