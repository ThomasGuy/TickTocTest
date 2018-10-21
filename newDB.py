import logging
import time

from ticktoctest.populate import Populate
from ticktoctest.models import Bitfinex_DB_Tables, Compare_DB_Tables
from ticktoctest.base import Session

log = logging.getLogger(__name__)


def main():
    tickToc = Populate(Bitfinex_DB_Tables, Compare_DB_Tables, '6h')
    tickToc.getin(Session, 'Database Created')


if __name__ == '__main__':
    main()
