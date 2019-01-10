import logging
import time

# package imports
from .base import engine, Session
from .cryptoAPIs import Compare, Bitfinex, Binance

log = logging.getLogger(__name__)


class Populate:
    """ Instances run for a sample frequency 'delta'.
    Collect data from Bitfinex and CryptoCompare, then save it to the Database """

    def __init__(self, Bitfinex_DB_Tables, Compare_DB_Tables, Binance_DB_Tables, delta):
        self.Bitfinex_DB_Tables = Bitfinex_DB_Tables
        self.Compare_DB_Tables = Compare_DB_Tables
        self.Binance_DB_Tables = Binance_DB_Tables
        self.dbTables = {**Bitfinex_DB_Tables, **Compare_DB_Tables, **Binance_DB_Tables}
        self.delta = delta

    def getin(self, msg, showCoins=False):
        """Running once, (frequency=delta) adds bulk rows to the Database"""

        with engine.begin() as conn:
            session = Session()
            try:
                compare = Compare(self.Compare_DB_Tables, self.delta)
                compare.chunk(session, conn)
            except Exception:
                session.rollback()
                log.error(f'CompareAPI "{self.delta}" Error', exc_info=True)
            finally:
                session.close()
                log.info(f'CompareAPI "{self.delta}" complete')

            session = Session()
            try:
                bitfinex = Bitfinex(self.Bitfinex_DB_Tables, self.delta)
                bitfinex.chunk(session, conn)
            except Exception:
                session.rollback()
                log.error(f'BitfinexAPI "{self.delta}" Error', exc_info=True)
            finally:
                session.close()
                log.info(f'BitfinexAPI "{self.delta}" complete')

            session = Session()
            try:
                binance = Binance(self.Binance_DB_Tables, self.delta)
                binance.chunk(session, conn)
            except Exception:
                session.rollback()
                log.error(f'BinanceAPI Error', exc_info=True)
            finally:
                session.close()
                log.info(f'BinanceAPI complete')

            log.info(f'"{self.delta}" {msg} update completed')
