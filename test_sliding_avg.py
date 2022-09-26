# todo: implement trailing stop for buy and sell orders
# todo: implement better dataset API

from Historic_Crypto import HistoricalData
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import utils

matplotlib.rcParams['backend'] = 'TkAgg'

# --- define general parameters ---
invested_money = 1000
cost_per_trade = 1
save_output = True
# --- define data parameter ---
start_date = '2019-09-01-00-00'
end_date = '2019-09-30-00-00'
freq = 60  # data frequency in seconds
# --- define model parameters ---
perc_band = 0.5  # in %
hours_window = 2  # in hours
spread = 0.1  # spread in % Difference between buy and sell order
avrg_type = 'mov_avrg'  # mov_avrg or abs_avrg

buy_val_list = []
buy_time_list = []
sell_val_list = []
sell_time_list = []
buy_val = None
sell_val = None

# len_window, time_delta = extract_window_length(hours=hours_window, data=raw_data)
len_window = int(3600 * hours_window / freq)
data = utils.get_data(len_window=len_window, freq=freq)

bandwidth = utils.calc_bandwidth(percentage=perc_band, init_avg=data[avrg_type][len_window])
init_buy, buy_index = utils.find_first_buy(data=data, bandwidth=bandwidth, len_window=len_window)
buy_val_list.append(init_buy + 0.5 * spread * 0.01 * init_buy)
buy_time_list.append(data.axes[0][buy_index])
sell_flag = False
for i in range(buy_index, len(data)):
    sell_val = utils.check_sell(open=data['open'][i], avg=data[avrg_type][i], buy_val=buy_val_list[-1],
                                bandwidth=bandwidth)
    if sell_val is not None and sell_flag is False:
        sell_val_list.append(sell_val - 0.5 * spread * 0.01 * sell_val)  # correct values with spread
        sell_time_list.append(data.axes[0][i])
        sell_flag = True
    if sell_val_list:
        buy_val = utils.check_buy(open=data['open'][i], avg=data[avrg_type][i], sell_val=sell_val_list[-1],
                                  bandwidth=bandwidth)
    if buy_val is not None and sell_flag:
        buy_val_list.append(buy_val + 0.5 * spread * 0.01 * buy_val)
        buy_time_list.append(data.axes[0][i])
        sell_flag = False

# calculate performance parameters of trading strategy
num_trades = len(buy_val_list) + len(sell_val_list)
sell_val_list = np.array(sell_val_list)
buy_val_list = np.array(buy_val_list)
win_trade_abs = sell_val_list - buy_val_list[0:len(sell_val_list)]
win_trade_perc = np.sum(win_trade_abs / sell_val_list) * 100
abs_profit = invested_money * win_trade_perc * 0.01 - num_trades * cost_per_trade

if save_output:
    delta = data.index.max() - data.index.min()
    time_delta = delta.total_seconds()
    file = open("Out-{}to{}.txt".format(start_date, end_date), "w")
    file.write(
        'date: {} to {} \n absolute time [hours]: {} \n num_trades: {} \n win_trade_perc [without order cost]: {}'
        ' \n invested_money: {} \n abs_profit:{} \n \n \n perc_band: {} \n hours_window: {} \n spread: {} '
        '\n avrg_type: {}'.format(start_date, end_date, time_delta / 60 ** 2, num_trades, win_trade_perc,
                                  invested_money, abs_profit, perc_band, hours_window, spread, avrg_type))
    file.close()
    plt.plot(data['open'], marker='o')
    plt.plot(data['mov_avrg'], marker='x')
    plt.plot(data['abs_avrg'], marker='x')
    plt.plot(buy_time_list, buy_val_list, marker='x', markersize=20, markeredgecolor='r', linestyle='None')
    plt.plot(sell_time_list, sell_val_list, marker='x', markersize=20, markeredgecolor='g', linestyle='None')
    plt.savefig('Fig-{}to{}'.format(start_date, end_date))
