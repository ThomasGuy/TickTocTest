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