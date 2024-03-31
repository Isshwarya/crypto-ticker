from sqlalchemy import DateTime, Column, Integer, String, Float
from lib.db.models import BASE


class CryptoPrice(BASE):
    __tablename__ = "crypto_price"

    id = Column(Integer, primary_key=True)
    symbol = Column(String(20))
    price = Column(Float())
    datetime = Column(DateTime())

    def __init__(self, symbol, price, datetime):
        self.symbol = symbol
        self.price = price
        self.datetime = datetime


class LatestCryptoPrice(BASE):
    __tablename__ = "latest_crypto_price"

    id = Column(Integer, primary_key=True)
    symbol = Column(String(20), unique=True)
    price = Column(Float())
    datetime = Column(DateTime())

    def __init__(self, symbol, price, datetime):
        self.symbol = symbol
        self.price = price
        self.datetime = datetime


class Settings(BASE):
    __tablename__ = 'settings'
    name = Column(String, primary_key=True)
    value = Column(String)

    def __init__(self, name, value):
        self.name = name
        self.value = value
