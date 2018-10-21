import logging
import time

# package imports
from .bitfinexAPI import BitfinexAPI
from .cryptoCompareAPI import CompareAPI


log = logging.getLogger(__name__)


class Populate:
    """ Instances run in their own thread each for a different sample frequency
    'delta'.
    Collect data from Bitfinex and CryptoCompare monitor it, then
    save it to the Database """
    def __init__(self, Bitfinex_DB_Tables, CryptoCompare_DB_Tables, delta):
        self.Bitfinex_DB_Tables = Bitfinex_DB_Tables
        self.CryptoCompare_DB_Tables = CryptoCompare_DB_Tables
        self.dbTables = {**Bitfinex_DB_Tables, **CryptoCompare_DB_Tables}
        self.delta = delta

    def getin(self, Session, msg, showCoins=False):
        """Running in it's own thread continually, (frequency=delta) adds a
         new row to the Database every delta"""

        interval = {'5m': 300, '15m': 900, '30m': 1800, '1h': 3600, '3h': 10800, '6h': 21600}
        bitfinexURL = 'https://api.bitfinex.com/v2/candles/trade:'
        compareURL = 'https://min-api.cryptocompare.com/data/histohour?'

        session = Session()
        try:
            CompareAPI.chunk(session, self.delta, compareURL,
                                interval, self.CryptoCompare_DB_Tables)
        except Exception:
            session.rollback()
            log.error(f'CompareAPI "{self.delta}" Error', exc_info=True)
        finally:
            session.close()
            # log.info(f'CompareAPI "{self.delta}" complete')

        session = Session()
        try:
            BitfinexAPI.chunk(session, self.delta, bitfinexURL,
                                interval, self.Bitfinex_DB_Tables)
        except Exception:
            session.rollback()
            log.error(f'BitfinexAPI "{self.delta}" Error', exc_info=True)
        finally:
            session.close()
            # log.info(f'BitfinexAPI "{self.delta}" complete')

        log.info(f'"{self.delta}" {msg} update completed')
