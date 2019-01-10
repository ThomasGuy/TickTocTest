import pandas as pd
import pymysql
from sqlalchemy import create_engine

from Altcoin.altcoin.getData import getData
from .tickToc import getDF
from .models import all_DB_tables, Base

test_coins = ['BTCUSD']
# can combine the '15m' and '1h' coins together
m15_coins = ['BCHUSD','BTCUSD', 'BTGUSD', 'DSHUSD', 'EOSUSD', 'ETCUSD',
             'ETHUSD', 'IOTUSD', 'LTCUSD', 'NEOUSD', 'OMGUSD',
             'TRXUSD', 'XMRUSD', 'XRPUSD', 'ZECUSD', 'QTMUSD', 'QSHUSD', 'SANUSD', 'GNTUSD']

h3_coins = ['SPKUSD', 'AVTUSD', 'FUNUSD', 'RCNUSD', 'RLCUSD']

db_15 = ['bab', 'xlm', 'ada', 'xem', 'ven', 'bnb', 'bcn', 'icx', 'ont', 'zil', 'ae', 'zrx']
db_1h = ['dcr', 'lsk', 'nano', 'steem', 'waves', 'xvg', 'elf']
db_3h = ['edo', 'mana']

binance = ['bchsv']

db_name = f'sqlite:///c:\\data\\sqlite\\db\\master_db.db'

master_db = 'sqlite:///c:\\data\\sqlite\\db\\master_db.db'
engine_master = create_engine(master_db, pool_recycle=3000, echo=False)
Base.metadata.create_all(engine_master)

tables = all_DB_tables()


def updateDB(df, table, conn):
    df.to_sql(con=conn, name=table.__tablename__, index=True, chunksize=100, if_exists='append')


def mergeMaster():
    with engine_master.begin() as conn:
        # Combine Altcoin with mysql ticktoc15m.db
        for coin in ['BCHUSD']:
            sym = coin[:-3]
            df1D = getData(sym, '1D')
            df6 = getData(sym, '6h')
            df1 = getData(sym, '1h')
            db_df = getDF(sym.lower(), db_name)

            DF = pd.concat([df1D, df6, df1, db_df])
            DF.drop_duplicates(inplace=True)
            DF = DF.groupby('MTS')['Open', 'Close', 'High', 'Low', 'Volume'].mean()
            DF.sort_values(by=['MTS'])
            DF.reset_index()

            updateDB(DF, tables[sym.lower()], conn)

        # for coin in h3_coins:
        #     sym = coin[:-3]
        #     df1D = getData(sym, '1D')
        #     df6 = getData(sym, '6h')
        #     df1 = getData(sym, '3h')
        #     db_df = getDF(sym.lower(), db_name)

        #     DF = pd.concat([df1D, df6, df1, db_df])
        #     DF.drop_duplicates(inplace=True)
        #     DF = DF.groupby('MTS')['Open', 'Close', 'High', 'Low', 'Volume'].mean()
        #     updateDB(DF, tables[sym.lower()], conn)

        # # All the rest of the coins from tickTock15m
        # for coins in [db_15, db_1h, db_3h, binance]:
        #     for coin in coins:
        #         DF = getDF(coin, db_name)
        #         DF.drop_duplicates(inplace=True)
        #         DF = DF.groupby('MTS')['Open', 'Close', 'High', 'Low', 'Volume'].mean()
        #         updateDB(DF, tables[coin], conn)


# we haven't included Bchsv from Binance
if __name__ == '__main__':
    mergeMaster()
