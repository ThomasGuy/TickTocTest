import pandas as pd
import logging
import matplotlib.pyplot as plt
import warnings

from .models import getTable

# log = logging.getLogger(__name__)


class Empty_Table(Exception):
    pass


def get_DataFrame(coin, session, **kwargs):
    """
    Return resampled datafram and oringinal data
    """
    default_options = {
        'sma': 10,
        'bma': 27,
        'lma': 74,
        'resample': '6H'
    }
    opts = dict(default_options)
    opts.update(kwargs)
    try:
        db_ = getTable(coin)
        data = session.query(db_.MTS, db_.Open, db_.Close, db_.High, db_.Low, db_.Volume).all()
        if data == []:
            raise Empty_Table
        df = pd.DataFrame(data)
        latest_timestamp = df['MTS'].max()
        df.set_index('MTS', drop=True, inplace=True)
        base = latest_timestamp.hour + latest_timestamp.minute / 60.0
        if not df.index.is_unique:
            df.drop_duplicates()
            df = df.groupby('MTS')['Open', 'Close', 'High', 'Low', 'Volume'].mean()
        resampledData = df.resample(rule=opts['resample'], closed='right', label='right', base=base).agg(
            {'Open': 'first', 'Close': 'last', 'High': 'max', 'Low': 'min', 'Volume': 'sum'})
        resampledData['sewma'] = resampledData['Close'].ewm(span=opts['sma']).mean()
        resampledData['bma'] = resampledData['Close'].rolling(span=opts['bma']).mean()
        resampledData['lma'] = resampledData['Close'].rolling(span=opts['lma']).mean()

    except Empty_Table as err:
        # log.error(
        #     f'Empty Table {coin} errors: {err.args}', exc_info=True)
        raise Empty_Table
    except Exception as err:
        raise(err)
    return (resampledData.iloc[opts['bma']:], df)


def _get_DF_Tables(session, DB_Tables, **kwargs):
    """Generate a DataFrame for each DB_Table, reasmple back from the present
    time i.e. the right of the sample frequency interval. Add in the moving averages
    """
    DF_Tables = {}
    for coin in DB_Tables.keys():
        resampledData, df = get_DataFrame(coin, session, **kwargs)
        DF_Tables[coin] = (resampledData, df)

    return DF_Tables


def _crossover(dataset):
    """Record any crossing points of the moving averages"""
    record = []
    # use 5th db record as 1st has equal SEWMA = BEWMA
    Higher = dataset.iloc[4]['sewma'] > dataset.iloc[4]['bma']
    # Initialize record ensures record is never empty
    if Higher:
        record.append([dataset.index[4], dataset['Close'].iloc[4], 'Buy'])
    else:
        record.append([dataset.index[4], dataset['Close'].iloc[4], 'Sell'])

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=RuntimeWarning)
        for date, row in dataset.iterrows():
            if Higher:
                # Sell condition
                if row['sewma'] / row['bma'] < 1:
                    record.append([date, row['Close'], 'Sell'])
                    Higher = not Higher
            else:
                # Buy condition
                if row['sewma'] / row['bma'] > 1:
                    record.append([date, row['Close'], 'Buy'])
                    Higher = not Higher

    cross = pd.DataFrame(record, columns=('Date Close Transaction').split())
    cross.set_index('Date', drop=True, inplace=True)
    return cross


def plotDataset(dataset, record, df, title):
    fig = plt.figure(figsize=(16, 8))
    axes = fig.add_axes([0, 0, 1, 1])
    # plot dataset
    axes.plot(dataset.index, dataset['sewma'], label='sma={}'.format(10), color='blue')
    axes.plot(dataset.index, dataset['bewma'], label='bma={}'.format(27), color='red')
    axes.plot(dataset.index, dataset['longewma'], label=f'longma={74}', color='orange', alpha=.5)
    axes.plot(df.index, df['Close'], label='close', color='green', alpha=.5)
    # axes.plot(df.index, df['High'], label='high', color='pink', alpha=.5)

    # plot the crossover points
    sold = pd.DataFrame(record[record['Transaction'] == 'Sell']['Close'])
    axes.scatter(sold.index, sold['Close'], color='r', label='Sell', lw=3)
    bought = pd.DataFrame(record[record['Transaction'] == 'Buy']['Close'])
    axes.scatter(bought.index, bought['Close'], color='g', label='Buy', lw=3)

    axes.set_ylabel('closing price')
    axes.set_xlabel('Date')
    axes.grid(color='b', alpha=0.5, linestyle='--', linewidth=0.5)
    axes.grid(True)
    axes.set_title(title + " - Latest price: ${:.4f}".format(df['Close'].iloc[-1]), fontsize=15)
    # axes.set_xticks()
    plt.legend()
    plt.show()
