import requests
import pandas as pd
import multiprocessing as mp
import settings


iex_p_api_token = settings.get_iex_p_api_token()
iex_s_api_token = settings.get_iex_s_api_token()


base_url = 'https://sandbox.iexapis.com/stable/'


quote_keep_keys = ('open',
                   'high',
                   'low',
                   'close',
                   'previousClose',
                   'volume',
                   'previousVolume',
                   'avgTotalVolume',
                   'changePercent')


def filter_for_keys(d, keep_keys):
    """filters out unnecessary keys from dictionary

    Args:
        d (dictionary): original dictionary
        keep_keys (iterable): any iterable that contains the keys we want to keep

    Returns:
        dictionary: contains only needed keeps
    """
    return {key: d[key] for key in keep_keys}


def get_eod_equities_data(ticker):
    """get quote for specific ticker

    Args:
        ticker (string): stock ticker

    Returns:
        dictionary that contains necessary data
    """
    url = base_url + f'stock/{ticker}/quote?token={iex_p_api_token}'
    json_response = requests.get(url).json()

    return filter_for_keys(json_response, quote_keep_keys)


def get_length_list(l, length):
    """ separates list l into lists of length

    Args:
        l (list):
        length (int): 

    Yields:
        list: of length
    """
    for i in range(0, len(l), length):
        yield l[i:i + length]


def get_eod_equities_data(tickers):

    d = {}
    for l_tickers in get_length_list(tickers, 100):
        s_symbols = ','.join(l_tickers)

        url = base_url + \
            f'stock/market/batch?symbols={s_symbols}&types=quote&token={iex_p_api_token}'

        json_response = requests.get(url).json()

        d_partial = {key: filter_for_keys(
            value['quote'], quote_keep_keys) for key, value in json_response.items()}

        d.update(d_partial)
    return d
