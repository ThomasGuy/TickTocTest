import sqlalchemy as sa
import pandas as pd
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import create_engine

from .models import Base, getTable
from .models import all_DB_tables
from .get_DF_Tables import _get_DF_Tables, _crossover, plotDataset, get_DataFrame

from datetime import timedelta
import matplotlib.pyplot as plt

Tables = all_DB_tables()
# db_name = 'mysql+pymysql://TomRoot:Sporty66@mysql.stackcp.com:51228/ticktoctestDB-3637742e'
master = f'sqlite:///c:\\data\\sqlite\\db\\master_db.db'


def db_session(db_name=master):
    """Returns the session"""
    engine = create_engine(db_name, pool_recycle=3000, echo=False)
    Session = scoped_session(sessionmaker(bind=engine))
    Base.metadata.create_all(engine)
    return Session


def getDBdata(coin, step, session):
    """
    Returns all the resampled data for that coin
    """
    # session = session or db_session()
    db_ = getTable(coin)
    data = session.query(db_.MTS, db_.Open, db_.Close, db_.High, db_.Low, db_.Volume).all()
    df = pd.DataFrame(data)
    df.sort_values('MTS', ascending=True)
    latest_timestamp = df['MTS'].max()
    df.drop_duplicates()
    df = df.groupby('MTS')['Open', 'Close', 'High', 'Low', 'Volume'].mean().reset_index()
    df.set_index('MTS', drop=True, inplace=True)
    base = latest_timestamp.hour + latest_timestamp.minute / 60.0
    resample_freq = step.upper()
    return df.resample(rule=resample_freq, closed='right', label='right', base=base).agg(
        {
            'Open': 'first',
            'Close': 'last',
            'High': 'max',
            'Low': 'min',
            'Volume': 'sum'
        })


def df_gen(tables, session):
    for table in tables:
        data = session.query(table.MTS, table.Open, table.Close, table.High, table.Low, table.Volume).all()
        df = pd.DataFrame(data)
        df.drop_duplicates()
        df = df.groupby('MTS')['Open', 'Close', 'High', 'Low', 'Volume'].mean()
        df.sort_values('MTS', ascending=True)
        yield (table.__tablename__, df)


def dfTables(session, DB_Tables=Tables):
    """Return all DF Tables"""
    return _get_DF_Tables(session, DB_Tables)


def df_cross_pair(coin, session, DB_Tables=Tables):
    """Return coin_df and cross_df"""
    dataset, df = get_DataFrame(coin, session)
    cross = _crossover(dataset)
    return (dataset, cross)


def dbTables():
    """Returns all the tictoc DB Tables"""
    return Tables


def dfTable(coin, session):
    """ Return a single DF Table """
    return get_DataFrame(coin, session)


def getDF(coin, session):
    db_ = getTable(coin)
    data = session.query(db_.MTS, db_.Open, db_.Close, db_.High, db_.Low, db_.Volume).all()
    df = pd.DataFrame(data)
    df.set_index('MTS', drop=True, inplace=True)
    return df


def rawDF(coin, session):
    db_ = getTable(coin)
    data = session.query(db_.MTS, db_.Open, db_.Close, db_.High, db_.Low, db_.Volume).all()
    return pd.DataFrame(data)
