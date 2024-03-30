import argparse
import asyncio
import re
from binance import AsyncClient, BinanceSocketManager
from datetime import datetime, timedelta
from pprint import pformat

import lib.logger as logger
from lib.db.client import Client
from lib.db.models.schema import CryptoPrice, LatestCryptoPrice
from lib.utils import every

class DataReceiver(object):

    def __init__(self, api_key, api_secret, interval, symbols,
                 db_name, db_host, db_user_name, db_password,
                 db_update_interval):
        self.api_key = api_key
        self.api_secret = api_secret
        self.symbols = re.split(r'\s*,\s*', symbols)
        self.capture_interval = interval
        self.db_update_interval = db_update_interval
        self.last_recorded = {}
        for symbol in self.symbols:
            self.last_recorded[symbol] = {
                "dt": datetime.now().replace(microsecond=0),
                "price": None,
                "id": None
            }
        
        # asyncio.run can be used if no other eventloops of asyncio are running
        client = asyncio.run(AsyncClient.create(self.api_key, self.api_secret))
        self.bm = BinanceSocketManager(client)
        self.loop = asyncio.get_event_loop()
        self.initialize_db(db_name, db_host, db_user_name, db_password)
        self.crypto_price_objects = []

    def initialize_db(self, db_name, db_host, db_user_name,db_password):
        self.db_client = Client(db_name=db_name, user_name=db_user_name,
                                password=db_password, host=db_host)
        self.db_client.connect()
        self.db_client.create_all_tables()
        # To initialize table with rows for each symbol so that later
        # we can always do "update" operation
        self.db_client.insert(LatestCryptoPrice, self.get_latest_crypto_price_objects(),
                             ignore_duplicates=True)
        rows = self.db_client.get_all(LatestCryptoPrice)
        for row in rows:
            self.last_recorded[row["symbol"]]["id"] = row["id"]

    def handle_socket_message(self, msg):
        symbol = msg['s']
        timestamp = msg['T']
        price = msg['p']
        trade_dt = datetime.fromtimestamp(timestamp / 1e3).replace(microsecond=0)
        
        if trade_dt >= self.last_recorded[symbol]["dt"] + timedelta(seconds=self.capture_interval):
            self.last_recorded[symbol]["dt"] = trade_dt
            self.last_recorded[symbol]["price"] = price
        else:
            # Nothing to do, as for this interval of the time, data was already
            # captured for the respective symbol.
            return

        # Create DB object
        self.crypto_price_objects.append(
            {
                "symbol": symbol,
                "price": price,
                "datetime": trade_dt
            }
        )
        logger.DEBUG(f"{trade_dt}: {symbol} ----> {price}")

    async def task_trade_socket(self, symbol):
        ts = self.bm.trade_socket(symbol)
        async with ts as trade_socket:
            while True:
                msg = await trade_socket.recv()
                self.handle_socket_message(msg)

    def flush_to_db(self):
        # No need for accessing self.crypto_price_objects with locks
        # as here we are dealing with cooperative multitasking (Coro)
        if self.crypto_price_objects:
            logger.DEBUG("Inserting %d records in DB" % (len(self.crypto_price_objects)))
            self.db_client.insert(CryptoPrice, self.crypto_price_objects)
            self.crypto_price_objects = []
        # Updating current latest price in a separate table so that
        # its super quick for the callers who need this info.
        # Indexing would be highly inefficient as the data gets updated for
        # every second and if we are indexing, it would be on (symbol, datetime)
        # and overhead on storage and processing would be high.
        # Also even to update the latest data in a separate table, triggers
        # were not chosen as we dont want the latest value to be updated for every
        # row insert, rather it should be done once for every group of objects
        # added together.
        if self.last_recorded[self.symbols[0]]["price"]:
            logger.DEBUG("Updating latest price table with data:\n%s" % 
                pformat(self.last_recorded, indent=2))
            self.db_client.update(LatestCryptoPrice, self.get_latest_crypto_price_objects())
        
    def get_latest_crypto_price_objects(self):
        latest_crypto_price_objects = []
        for symbol, details in self.last_recorded.items():
            data = {
                "symbol": symbol,
                "price": details["price"],
                "datetime": details["dt"],
            }
            if details["id"]:
                data["id"] = details["id"]
            latest_crypto_price_objects.append(data)
        return latest_crypto_price_objects
        
    def do_work(self):
        try:
            for symbol in self.symbols:
                asyncio.ensure_future(self.task_trade_socket(symbol=symbol))
            asyncio.ensure_future(every(self.db_update_interval, self.flush_to_db))
            self.loop.run_forever()
        except KeyboardInterrupt:
            logger.INFO("Keyboard Interrupt received")
        finally:
            logger.INFO("Closing Loop")
            self.loop.close()
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="A script to capture data for cryptocurrency symbols from Binance")
    parser.add_argument("-k", "--api_key",
                        help='API Key to access Binance APIs',
                        type=str, required=True)
    parser.add_argument("-s", "--api_secret",
                        help='Secret Key to access Binance APIs',
                        type=str, required=True)
    parser.add_argument("-c", "--cryptocurrency_symbols",
                        help='List of Cryptocurrency symbols separated by comma',
                        type=str, default="BNBBTC,BTCUSDT,ETHUSDT")
    parser.add_argument("-i", "--interval",
                        help='Interval for data capturing in seconds. Default: 1',
                        type=int, default=1)
    parser.add_argument("-r", "--db_update_interval",
                        help='Interval for updating the captured price data '
                             'to DB in seconds. Default: 5',
                        type=int, default=5)
    parser.add_argument("-o", "--db_host",
                        help='DB Host',
                        type=str, required=True)
    parser.add_argument("-n", "--db_name",
                        help='DB Name',
                        type=str, required=True)
    parser.add_argument("-u", "--db_user_name",
                        help='Username to access DB',
                        type=str, required=True)
    parser.add_argument("-p", "--db_password",
                        help='Password to access DB',
                        type=str, required=True)
    parser.add_argument("-d", "--debug", help="Enable debug messages",
                        required=False, action='store_true')
    parsed_args = parser.parse_args()
    if parsed_args.debug:
        logger.setup_logging(log_level="DEBUG")
    receiver = DataReceiver(
        api_key=parsed_args.api_key,
        api_secret=parsed_args.api_secret,
        symbols=parsed_args.cryptocurrency_symbols,
        interval=parsed_args.interval,
        db_name=parsed_args.db_name,
        db_host=parsed_args.db_host,
        db_user_name=parsed_args.db_user_name,
        db_password=parsed_args.db_password,
        db_update_interval=parsed_args.db_update_interval
    )
    receiver.do_work()
