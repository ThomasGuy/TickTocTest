import sqlalchemy as sa
import pandas as pd
from sqlalchemy.orm import sessionmaker, scoped_session

from .models import Base, BaseModel, getTable
from .models import all_DB_tables
from .get_DF_Tables import _get_DF_Tables, _crossover, plotDataset, get_DataFrame

from datetime import timedelta
import matplotlib.pyplot as plt

Tables = all_DB_tables()
# db_name = 'mysql+pymysql://TomRoot:Sporty66@mysql.stackcp.com:51228/ticktoctestDB-3637742e'
db_name = f'sqlite:///c:\\data\\sqlite\\db\\tickToc15m.db'


def db_session(db_name=db_name):
    """Returns the session"""
    engine = sa.create_engine(db_name, pool_recycle=3500, echo=False)
    session = scoped_session(sessionmaker(bind=engine))
    Base.metadata.create_all(engine)
    BaseModel.set_session(session)
    return session


def getDBdata(coin, step, session=None):
    """
    Returns all the resampled data for that coin
    """
    session = session or db_session()
    db_ = getTable(coin)
    data = session.query(db_.MTS, db_.Open, db_.Close, db_.High, db_.Low, db_.Volume).all()
    df = pd.DataFrame(data)
    latest_timestamp = df['MTS'].max()
    df.set_index('MTS', drop=True, inplace=True)
    base = latest_timestamp.hour + latest_timestamp.minute / 60.0
    df.drop_duplicates()
    df = df.groupby('MTS')['Open', 'Close', 'High', 'Low', 'Volume'].mean()
    resample_freq = step.upper()
    return df.resample(rule=resample_freq, closed='right', label='right', base=base).agg(
        {'Open': 'first', 'Close': 'last', 'High': 'max', 'Low': 'min', 'Volume': 'sum'})


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


def getDF(coin, db_name=db_name):
    session = db_session(db_name)
    db_ = getTable(coin)
    data = session.query(db_.MTS, db_.Open, db_.Close, db_.High, db_.Low, db_.Volume).all()
    df = pd.DataFrame(data)
    return df.drop_duplicates()
