import sqlalchemy as sa
import pandas as pd
from sqlalchemy.orm import sessionmaker, scoped_session

from .models import Base, BaseModel, getTable
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


def getDBdata(coin, step, session=None):
    """
    Returns all the resampled data for that coin
    """
    session = session or db_session()
    db_ = getTable(coin)
    data = session.query(db_.MTS, db_.Open, db_.Close, db_.High, db_.Low, db_.Volume).all()
    df = pd.DataFrame([[item for item in tpl] for tpl in data],
                        columns=('MTS', 'Open', 'Close', 'High', 'Low', 'Volume'))
    latest_timestamp = df['MTS'].max()
    df.set_index('MTS', drop=True, inplace=True)
    base = latest_timestamp.hour + latest_timestamp.minute / 60.0
    df.drop_duplicates()
    df = df.groupby('MTS')['Open', 'Close', 'High', 'Low', 'Volume'].mean()
    resample = step.upper()
    resampled = df.resample(rule=resample, closed='right', label='right', base=base).agg(
        {'Open': 'first', 'Close': 'last', 'High': 'max', 'Low': 'min', 'Volume': 'mean'})
    return resampled.rename({'Open': 'open', 'Close': 'close', 'High': 'high', 'Low': 'low',
                            'Volume': 'volume'}, axis=1)


def plot(coin, session=None, start=None, finish=None, title='', **kwargs):
    """plot coin with buy sell points"""
    session = session or db_session()
    dataset, df = get_DataFrame(coin, session, **kwargs)
    # lop off the first week to let the ewma's get settled
    cross = _crossover(dataset)
    if start is None:
        start = (dataset.index[0] + timedelta(7)).strftime('%Y-%m-%d')

    plotDataset(dataset.loc[start:finish], cross.loc[start:finish], df.loc[start:finish], title)


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


def candles(coin, period=30, session=None, title='', **kwargs):
    opts = {
        'resample': '1D',
        'sma': 4,
        'bma': 7,
        'lma': 19
    }
    opts.update(kwargs)
    session = session or db_session()
    title = title or coin.capitalize()
    dataset, df = get_DataFrame(coin, session, resample=opts['resample'], sma=opts['sma'], bma=opts['bma'],
                                lma=opts['lma'])
    start = (dataset.index[-1] - timedelta(period)).strftime('%Y-%m-%d')
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
    ax.set_title(title + "  last price: ${:.4f}".format(df['Close'].iloc[-1]), fontsize=15)

    candlestick_ohlc(ax, data_values, width=0.6, colorup='g', colordown='r')

    # plt.setp(plt.gca().get_xticklabels(), rotation=45, horizontalalignment='right')

    ax.plot(data.date_ax, data['sewma'], label='sma={}'.format(opts['sma']), color='blue')
    ax.plot(data.date_ax, data['bewma'], label='bma={}'.format(opts['bma']), color='purple')
    ax.plot(data.date_ax, data['longewma'], label='longma={}'.format(opts['lma']), color='orange', alpha=.5)
    plt.legend()
    plt.show()
