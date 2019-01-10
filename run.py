import logging
import time

from ticktoctest.populate import Populate
from ticktoctest.models import Bitfinex_DB_Tables, Compare_DB_Tables, Binance_DB_Tables

log = logging.getLogger(__name__)


def main():
    populateDB = Populate(Bitfinex_DB_Tables, Compare_DB_Tables, Binance_DB_Tables, '1h')
    populateDB.getin('Database UpDated')


if __name__ == '__main__':
    pass
    # main()
