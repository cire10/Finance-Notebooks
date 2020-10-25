import concurrent
import configparser
import requests
import datetime
import json
import time
import pathlib
import pandas as pd

config = configparser.ConfigParser()
config.optionxform = str
config.read('config.ini')

json_calls_chains_key = 'callExpDateMap'
json_puts_chains_key = 'putExpDateMap'


class OptionChain():

    @staticmethod
    def get_dte(str_expiry):
        return int(str_expiry[str_expiry.find(':')+1:])

    @staticmethod
    def get_expiration_dates(json_data):
        # prelim check if the expiries for puts and calls are matching
        # discard 0dte data
        call_expiries = [
            expiries for expiries in json_data[json_calls_chains_key].keys()]
        put_expiries = [
            expiries for expiries in json_data[json_puts_chains_key].keys()]
        if call_expiries == put_expiries:
            expiries = []
            for expiry in call_expiries:
                dte = OptionChain.get_dte(expiry)
                if dte != 0:
                    expiries.append(expiry)
            return expiries
        else:
            raise Exception('call expiries do not match put expiries')

    @staticmethod
    def get_option_chain_df(json_data, expiry):
        calls = json_data[json_calls_chains_key][expiry]
        puts = json_data[json_puts_chains_key][expiry]

        def get_list_options(chain):
            list_options = []
            list_options_append = list_options.append
            for strike_price, option_info in chain.items():
                list_options_append(option_info[0])
            return list_options

        df_calls = pd.DataFrame(get_list_options(calls))
        df_puts = pd.DataFrame(get_list_options(puts))
        df = df_calls.append(df_puts, ignore_index=True)
        return df

    @staticmethod
    def dict_option_chain_dfs_from_json(json_data):
        """
        docstring
        """
        expiries = OptionChain.get_expiration_dates(json_data)
        d = {}
        for expiry in expiries:
            d[expiry] = OptionChain.get_option_chain_df(json_data, expiry)
        return d


def _get_tos_option_params():
    """static tos api params 

    Returns:
        [dictionary]: [api params]
    """
    apikey = config['ToS']['api_key']
    params = {'apikey': apikey}
    return params


def _load_json_file(file_path):
    """loads data from json file pointed to by the file_path

    Args:
        file_path ([string]): [file path]

    Returns:
        [string, json]: [time of data, data]
    """
    time = file_path.with_suffix('').name
    with open(str(file_path)) as f:
        data = json.load(f)
    return time, data


def _get_all_json_files_paths(folder_name):
    """gets all json files paths in a single folder

    Args:
        folder_name ([string]): [description]

    Returns:
        [type]: [description]
    """
    list_json_files = []
    folder_path = pathlib.Path(
        __file__).parent.absolute().joinpath(folder_name)
    for file_name in folder_path.glob('*.json'):
        list_json_files.append(file_name)

    # sorting the files by time created, useful for dictionary construction
    list_json_files = sorted(list_json_files, key=lambda x: x.stat().st_ctime)
    return list_json_files


def get_all_intraday_jsons(date):
    """gets all option chains jsons saved for one date

    Args:
        date ([string]): [data date]

    Returns:
        [dictionary]: [time of data: json data]
    """
    list_json_files = _get_all_json_files_paths(date)
    d_json_option_chains = {}
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = executor.map(_load_json_file, list_json_files)
        for time, data in results:
            d_json_option_chains[time] = data
    return d_json_option_chains


def query_api_intraday_option_chains():
    """hack to query the api every 5 minutes without using cron
    """
    while True:
        json_option_chains = query_api_option_chains()
        save_json_option_chains(json_option_chains)
        time.sleep(300)


def query_api_option_chains(ticker):
    """query the ToS API to get ticker's latest option chains

    Args:
        ticker ([string])

    Returns:
        [json]: [json structure that contains option chains data]
    """
    url = 'https://api.tdameritrade.com/v1/marketdata/chains'
    params = _get_tos_option_params()
    params['symbol'] = ticker
    json_option_chain = requests.get(
        url, params=params).json()
    return json_option_chain


def save_json_option_chains(json_option_chains):
    """saves a json structure option chains to the local folder

    Args:
        json_option_chains ([json]): [option chains]
    """
    str_today_dtime = datetime.datetime.today().strftime('%Y%m%d %H%M%S')
    file_name = f'{str_today_dtime}.json'
    with open(file_name, 'w', encoding='utf-8') as f:
        json.dump(json_option_chains, f, ensure_ascii=False, indent=4)
