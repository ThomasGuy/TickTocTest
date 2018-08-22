import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker, scoped_session

from .models import Base, BaseModel
from .models import all_DB_tables
from .get_DF_Tables import _get_DF_Tables, _crossover, plotDataset, get_DataFrame

from datetime import timedelta
from mpl_finance import candlestick_ohlc
from matplotlib.dates import DateFormatter, date2num, WeekdayLocator, DayLocator, MONDAY
import matplotlib.pyplot as plt

Tables = all_DB_tables()
db_name = 'tickToc15m'


def db_session(db_name=db_name):
    """Returns the session"""
    _db = f'sqlite:///c:\\data\\sqlite\\db\\{db_name}.db'
    engine = sa.create_engine(_db, echo=False)
    session = scoped_session(sessionmaker(bind=engine))
    Base.metadata.create_all(engine)
    BaseModel.set_session(session)
    return session


def plot(coin, session=None, start=None, finish=None, title='', **kwargs):
    """plot coin with buy sell points"""
    session = session or db_session()
    dataset, df = get_DataFrame(coin, session, **kwargs)
    # lop off the first week to let the ewma's get settled
    cross = _crossover(dataset)
    # if start is None:
    #     start = (dataset.index[0] + timedelta(7)).strftime('%Y-%m-%d')

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


def candles(coin, session=None, title=''):
    sma = 4
    bma = 7
    lma = 19
    session = session or db_session()
    dataset, df = get_DataFrame(coin, session, resample='1D', sma=sma, bma=bma, lma=lma)
    start = (dataset.index[-1] - timedelta(90)).strftime('%Y-%m-%d')
    data = dataset.loc[start:].copy().reset_index()
    data['date_ax'] = data['MTS'].apply(lambda date: date2num(date))
    data_values = [tuple(vals) for vals in data[['date_ax', 'Open', 'High', 'Low', 'Close']].values]
    mondays = WeekdayLocator(MONDAY)        # major ticks on the mondays
    alldays = DayLocator()              # minor ticks on the days
    weekFormatter = DateFormatter('%b %d')  # e.g., Jan 12

    fig, ax = plt.subplots(figsize=(18, 8))
    fig.subplots_adjust(bottom=0.2)
    ax.xaxis.set_major_locator(mondays)
    ax.xaxis.set_minor_locator(alldays)
    ax.xaxis.set_major_formatter(weekFormatter)
    ax.autoscale_view()
    ax.xaxis.grid(True, 'major')
    ax.grid(True)
    ax.set_facecolor('lightgrey')
    ax.set_title(title + f"  last price: ${df['Close'].iloc[-1]}", fontsize=15)

    candlestick_ohlc(ax, data_values, width=0.6, colorup='g', colordown='r')

    # plt.setp(plt.gca().get_xticklabels(), rotation=45, horizontalalignment='right')

    ax.plot(data.date_ax, data['sewma'], label='ewma={}'.format(sma), color='blue')
    ax.plot(data.date_ax, data['bewma'], label='ewma={}'.format(bma), color='purple')
    ax.plot(data.date_ax, data['longewma'], label=f'longma={lma}', color='orange', alpha=.5)
    plt.legend()
    plt.show()
