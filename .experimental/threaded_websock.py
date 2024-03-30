import os
import json
from datetime import datetime, timedelta
import websocket as wb
from pprint import pprint
from binance import ThreadedWebsocketManager
from binance.client import Client
from binance.enums import *
from dotenv import load_dotenv


# load environment variables
load_dotenv()

API_KEY = os.environ.get("API_KEY")
API_SECRET = os.environ.get("API_SECRET")
client = Client(API_KEY, API_SECRET, tld='us')
twm = ThreadedWebsocketManager(api_key=API_KEY, api_secret=API_SECRET)
twm.start()
symbol1 = "BNBBTC"
symbol2 = "BTCUSDT"
symbol3 = "ETHUSDT"
last_recorded = {symbol1: None, symbol2: None, symbol3: None}


def handle_socket_message(msg):
    symbol = msg['s']
    timestamp = msg['T']
    trade_dt = datetime.fromtimestamp(timestamp / 1e3)
    # if not last_recorded[symbol]:
    #     last_recorded[symbol] = trade_dt
    # else:
    #     if trade_dt >= last_recorded[symbol] + timedelta(seconds=1):
    #         last_recorded[symbol] = trade_dt
    #     else:
    #         # Nothing to do, this value need not be captured
    #         return

    print(f"{trade_dt}: {symbol} ----> {msg['p']}")
    




twm.start_trade_socket(callback=handle_socket_message, symbol=symbol1)
twm.start_trade_socket(callback=handle_socket_message, symbol=symbol2)
twm.start_trade_socket(callback=handle_socket_message, symbol=symbol3)
twm.join()
