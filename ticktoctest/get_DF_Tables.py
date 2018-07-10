import pandas as pd
import logging
import matplotlib.pyplot as plt
import warnings

from .models import getTable

log = logging.getLogger(__name__)


class Empty_Table(Exception):
    pass


def get_DataFrame(coin, session, resample='6H', sma=10, bma=27, lma=74, **kwargs):
	db_  = getTable(coin)
	data = session.query(db_.MTS, db_.Open, db_.Close, db_.High, db_.Low).all()
	df = pd.DataFrame([[item for item in tpl] for tpl in data],
					columns=('MTS', 'Open', 'Close', 'High', 'Low'))
	latest_timestamp = df['MTS'].max()
	base = latest_timestamp.hour + latest_timestamp.minute/60.0
	df.set_index('MTS', drop=True, inplace=True)
	df.drop_duplicates()
	df = df.groupby('MTS')['Open', 'Close', 'High', 'Low'].mean()
	df = df.resample(rule=resample, closed='right', label='right', base=base).agg(
		{'Open': 'first', 'Close': 'last', 'High': 'max', 'Low': 'min'})
	df['sewma'] = df['Close'].ewm(span=sma).mean()
	df['bewma'] = df['Close'].ewm(span=bma).mean()
	df['longewma'] = df['Close'].ewm(span=lma).mean()
	return df


def _get_DF_Tables(session, DB_Tables, resample='6H', sma=10, bma=27, lma=74, **kwargs):
	"""Generate a DataFrame for each DB_Table, reasmple back from the present
	time i.e. the right of the sample frequency interval. Add in the moving averages
	"""
	DF_Tables = {}
	try:
		for i, table in DB_Tables.items():
			data = session.query(table.MTS, table.Open, table.Close,
								table.High, table.Low).all()
			df = pd.DataFrame([[item for item in tpl] for tpl in data],
							columns=('MTS', 'Open', 'Close', 'High', 'Low'))
			latest_timestamp = df['MTS'].max()
			base = latest_timestamp.hour + latest_timestamp.minute/60.0
			df.set_index('MTS', drop=True, inplace=True)
			df.drop_duplicates()
			df = df.groupby('MTS')['Open', 'Close', 'High', 'Low'].mean()
			df = df.resample(rule=resample, closed='right', label='right', base=base).agg(
				{'Open': 'first', 'Close': 'last', 'High': 'max', 'Low': 'min'})
			df['sewma'] = df['Close'].ewm(span=sma).mean()
			df['bewma'] = df['Close'].ewm(span=bma).mean()
			df['longewma'] = df['Close'].ewm(span=lma).mean()
			DF_Tables[i] = df
	except AttributeError:
		log.error(f'{i} in {table} ', exc_info=True)
	except Empty_Table as err:
		log.error(
			f'Empty Table {i} in {table} errors: {err.args}', exc_info=True)
		raise Empty_Table
	except Exception as err:
		raise(err)
	return DF_Tables


def _crossover(dataset):
	"""Record any crossing points of the moving averages"""
	record = []
	# use 5th db record as 1st has equal SEWMA = BEWMA
	Higher = dataset.iloc[4]['sewma'] > dataset.iloc[4]['bewma']
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
				if row['sewma'] / row['bewma'] < 1:
					record.append([date, row['Close'], 'Sell'])
					Higher = not Higher
			else:
				# Buy condition
				if row['sewma'] / row['bewma'] > 1:
					record.append([date, row['Close'], 'Buy'])
					Higher = not Higher

	cross = pd.DataFrame(record, columns=('Date Close Transaction').split())
	cross.set_index('Date', drop=True, inplace=True)
	return cross


def plotDataset(dataset, record, title):
    fig = plt.figure(figsize=(16, 8))
    axes = fig.add_axes([0, 0, 1, 1])
    # plot dataset
    axes.plot(dataset.index, dataset['sewma'],
              label='ewma={}'.format(10), color='blue')
    axes.plot(dataset.index, dataset['bewma'],
              label='ewma={}'.format(27), color='red')
    axes.plot(dataset.index, dataset['Close'],
              label='close', color='green', alpha=.5)
    axes.plot(dataset.index, dataset['longewma'],
              label=f'longma={74}', color='orange', alpha=.5)
    axes.plot(dataset.index, dataset['High'],
              label='high', color='pink', alpha=.5)

    # plot the crossover points
    sold = pd.DataFrame(record[record['Transaction'] == 'Sell']['Close'])
    axes.scatter(sold.index, sold['Close'], color='r', label='Sell', lw=3)
    bought = pd.DataFrame(record[record['Transaction'] == 'Buy']['Close'])
    axes.scatter(bought.index, bought['Close'], color='g', label='Sell', lw=3)

    axes.set_ylabel('closing price')
    axes.set_xlabel('Date')
    axes.grid(color='b', alpha=0.5, linestyle='--', linewidth=0.5)
    axes.grid(True)
    axes.set_title(title)
    # axes.set_xticks()
    plt.legend()
    plt.show()
