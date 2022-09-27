import pandas as pd
import yfinance as yf

#ssh test

# todo get data returns only timestamps and values and used avg
def get_data(stock_name: str) -> str:
    """
    desc

    :param stock_name: description
    :return:
    :rtype: str
    """
    stock = 's'
    return stock


A = get_data
B = 1


def find_first_buy(data, bandwidth, len_window):
    first_buy = None
    i = None
    for i in range(len_window, len(data)):
        if data['open'][i] < data[avrg_type][i] - bandwidth:
            first_buy = data['open'][i]
            return first_buy, i
    if first_buy is None:
        raise ValueError('Found no first buy point.')
    return first_buy, i


# todo check if this is correct (bandwidth should change at higher prices)
def calc_bandwidth(percentage, init_avg):
    return percentage * 0.01 * init_avg


def check_sell(open, avg, buy_val, bandwidth):
    if (open > buy_val + bandwidth) and (open > avg + bandwidth):
        return open


def check_buy(open, avg, sell_val, bandwidth):
    if (open < sell_val + bandwidth) and (open < avg - bandwidth):
        return open
