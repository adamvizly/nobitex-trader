import json
import requests
import pyotp
import config
import pandas as pd
from datetime import datetime, timedelta


class Nobitex:
    
    token = ''


    def __init__(self):
        self.baseurl = config.nobitex['baseurl']
        self.username = config.nobitex['username']
        self.password = config.nobitex['password']
        self.authkey = config.nobitex['authkey']


    def get_2fa(self):
        totp = pyotp.TOTP(self.authkey)
        return totp.now()


    def login(self):
        url = self.baseurl + 'auth/login/'

        payload = {
            'username': self.username,
            'password': self.password,
            'remember': 'yes',
            'captcha': 'api'
        }
        headers = {
            'X-TOTP': self.get_2fa()
        }
        response = requests.request("POST", url, data=payload, headers=headers)
        response = response.json()
        print('logged in successfully.')
        self.token = response['key']


    def place_order(self, market, amount, price, fast=True, buy=True):
        if market.endswith('IRT'):
            src = market[:-3].lower()
            dst = 'rls'
        else:
            src = market[:-4].lower()
            dst = 'usdt'
        url = self.baseurl + 'market/orders/add'
        payload = json.dumps({
        'type': 'buy' if buy else 'sell',
        'execution': 'market' if fast else 'limit',
        'srcCurrency': src,
        'dstCurrency': dst,
        'amount': amount,
        'price': price
        })
        headers = {
        'Authorization': f'Token {self.token}',
        'content-type': 'application/json'
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        response = response.json()
        return response


    def check_orders(self, market):
        pass


    def get_ohlc(self, market, resolution, start , end):
        start = int(start.timestamp())
        end = int(end.timestamp())
        url = self.baseurl + f'market/udf/history?symbol={market}&resolution={resolution}&from={start}&to={end}'
        response = requests.request("GET", url)
        print(url)
        response = response.json()
        df = pd.DataFrame(list(zip(
            response['t'], response['c'], response['o'],
            response['h'],response['l'],response['v']
            )), columns=['time', 'close', 'open', 'high', 'low', 'volume'])
        return df

