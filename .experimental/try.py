import os
import json
from datetime import datetime
import websocket as wb
from pprint import pprint
from binance.client import Client
from binance.enums import *
from dotenv import load_dotenv


# load environment variables
load_dotenv()


BINANCE_SOCKET = "wss://stream.binance.com:9443/ws/bnbbtc@trade"


API_KEY = os.environ.get("API_KEY")
API_SECRET = os.environ.get("API_SECRET")
# client = Client(API_KEY, API_SECRET, tld='us')


def on_open(ws):
    print("connection opened")


def on_close(ws):
    print("closed connection")


def on_error(ws, error):
    print(error)


def on_message(ws, message):
    message = json.loads(message)
    pprint(message)
    # candle = message['k']
    # trade_symbol = message['s']
    # is_candle_closed = candle['x']
    # global closed_prices
    # if is_candle_closed:
    #     symbol = candle['s']
    #     closed = candle['c']
    #     open = candle['o']
    #     high = candle['h']
    #     low = candle['l']
    #     volume = candle['v']

    #     closed_prices.append(float(closed))

    #     data = {"crypto_name": symbol, "open_price": open, "close_price": closed,
    #             "high_price": high, "low_price": low, "volume": volume, "time": datetime.utcnow()}
    #     pprint(data)


ws = wb.WebSocketApp(BINANCE_SOCKET, on_open=on_open,
                     on_close=on_close, on_error=on_error, on_message=on_message)
ws.run_forever()
