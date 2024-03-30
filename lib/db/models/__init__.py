from sqlalchemy.ext.declarative import declarative_base
from .crypto_price import CryptoPrice
from .latest_crypto_price import LatestCryptoPrice

BASE = declarative_base()