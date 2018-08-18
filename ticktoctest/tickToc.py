import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker, scoped_session

from .models import Base, BaseModel
from .models import all_DB_tables
from .get_DF_Tables import _get_DF_Tables, _crossover, plotDataset, get_DataFrame

from datetime import timedelta

Tables = all_DB_tables()
db_name = 'tickToc15m'


def plot(coin, session, start=None, finish=None, title='', **kwargs):
    """plot coin with buy sell points"""
    dataset, df = get_DataFrame(coin, session, **kwargs)
    # lop off the first week to let the ewma's get settled
    cross = _crossover(dataset)
    if start is None:
        start = (dataset.index[0] + timedelta(7)).strftime('%Y-%m-%d')

    plotDataset(dataset.loc[start:finish], cross.loc[start:finish], df.loc[start:finish], title)


def dfTables(session, DB_Tables=Tables, **kwargs):
    """Return all DF Tables"""
    return _get_DF_Tables(session, DB_Tables, **kwargs)


def df_cross_pair(coin, session, DB_Tables=Tables, **kwargs):
    """Return coin_df and cross_df"""
    # DF_Tables = _get_DF_Tables(session, DB_Tables, **kwargs)
    dataset, df = get_DataFrame(coin, session)
    cross = _crossover(dataset)
    return (dataset, cross)


def dbTables():
    """Returns all the tictoc DB Tables"""
    return Tables


def dfTable(coin, session):
    """ Return a single DF Table """
    return get_DataFrame(coin, session)


def db_session(db_name=db_name):
    """Returns the session"""
    _db = f'sqlite:///c:\\data\\sqlite\\db\\{db_name}.db'
    engine = sa.create_engine(_db, echo=False)
    session = scoped_session(sessionmaker(bind=engine))
    Base.metadata.create_all(engine)
    BaseModel.set_session(session)
    return session


# def switchToTimestamp():
# 	session = db_session()
# 	for table in Tables.values():
# 		data = session.query(table).all()
