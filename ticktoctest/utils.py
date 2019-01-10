"""
Provides utility functions used across more than one module or sub module.

"""

# Import Built-Ins
import logging
import json
import sys
import time
import smtplib
import warnings

# Import Third-Party
import requests
import pandas as pd


# Init Logging Facilities
log = logging.getLogger(__name__)


class Error_429(Exception):
    pass


class Empty_Table(Exception):
    pass


# get request response from exchange api
class Return_API_response:
    """Get data from BitFinex API. Bitfinex rate limit policy can vary in a
     range of 10 to 90 requests per minute. So if we get a 429 response wait
     for a minute"""
    def __init__(self):
        self.sesh = requests.Session()

    def api_response(self, url):
        try:
            res = self.sesh.get(url)
            data = res.json()
            if res.status_code == 429:
                raise Error_429

            res.raise_for_status()
        except Error_429 as err:
            raise Error_429
        except requests.exceptions.HTTPError as err:
            log.info(f'Raise_for_status: {err.__class__.__name__}')
            raise err

        return data

    def close_session(self):
        self.sesh.close()


class DF_Tables:
    """Generate a DataFrame for each DB_Table, reasmple back from the present
    time i.e. the right of the sample frequency interval. Add in the moving averages
    """
    # Note I use the same dictionary index for DB, DF and altcoins

    @staticmethod
    def get_DFTables(session, dbTables, sma=10, bma=27, lma=74, resample='6H'):
        DF_Tables = {}

        try:
            for i, table in dbTables.items():
                data = session.query(table.MTS, table.Open, table.Close, table.High, table.Low).all()
                if data == []:
                    raise Empty_Table
                df = pd.DataFrame(data)
                df.set_index('MTS', drop=True, inplace=True)
                latest_timestamp = df.index.max()
                base = latest_timestamp.hour + latest_timestamp.minute / 60.0
                df.drop_duplicates()
                df = df.groupby('MTS')['Open', 'Close', 'High', 'Low'].mean()

                df = df.resample(rule=resample, closed='right', label='right', base=base). \
                            agg({'Open': 'first', 'Close': 'last', 'High': 'max', 'Low': 'min'})

                df['sewma'] = df['Close'].ewm(span=sma).mean()
                df['bma'] = df['Close'].rolling(bma).mean()
                df['lma'] = df['Close'].rolling(lma).mean()
                DF_Tables[i] = df
        except AttributeError:
            log.error(f'{i} in {table} ', exc_info=True)
        except Empty_Table as err:
            log.info(f'Empty Table {i} in {table} errors: {err.args}', exc_info=True)
        except Exception as err:
            raise(err)
        finally:
            session.close()

        return DF_Tables

    @staticmethod
    def crossover(dataset):
        """From DataFrame 'dataset'. Return a DataFrame of all the crossing points
         of the small and medium moving averages"""

        record = []
        Higher = dataset.iloc[0]['sewma'] > dataset.iloc[0]['bma']
        # initialize record[] ensures record is never empty
        if Higher:
            record.append([dataset.index[0], dataset['Close'].iloc[0], 'Buy'])
        else:
            record.append([dataset.index[0], dataset['Close'].iloc[0], 'Sell'])

        # Catch Numpy warning
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=RuntimeWarning)
            for date, row in dataset.iterrows():
                if Higher:
                    # Sell condition
                    if row['sewma'] / row['bma'] < 0.9965:
                        record.append([date, row['Close'], 'Sell'])
                        Higher = not Higher
                else:
                    # Buy condition
                    if row['sewma'] / row['bma'] > 1.0035:
                        record.append([date, row['Close'], 'Buy'])
                        Higher = not Higher

        cross = pd.DataFrame(record, columns=('Date Close Transaction').split())
        cross.set_index('Date', drop=True, inplace=True)
        return cross
