from Historic_Crypto import HistoricalData
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import numpy as np

matplotlib.rcParams['backend'] = 'TkAgg'

start_date = '2019-01-09-00-00'
end_date = '2019-01-10-00-00'

def get_data(len_window, freq):
    list = pd.DataFrame(HistoricalData('ETH-USD', freq, start_date, end_date).retrieve_data())
    del list['low']
    del list['high']
    del list['close']
    del list['volume']
    list['mov_avrg'] = list['open'].rolling(len_window).mean()
    list['abs_avrg'] = list['open'].mean()
    return list


def find_first_buy(data, bandwidth, len_window):
    first_buy = None
    i = None
    for i in range(len_window, len(data)):
        if data['open'][i] < data[avrg_type][i] - bandwidth:
            first_buy = data['open'][i]
            return first_buy, i
    if first_buy == None: raise ValueError('Found no first buy point.')
    return first_buy, i


def calc_bandwidth(percentage, init_avg):
    return percentage*0.01*init_avg


def check_sell(open, avg, buy_val, bandwidth):
    if (open > (buy_val + bandwidth)) and (open > (avg + bandwidth)):
        return open


def check_buy(open, avg, sell_val, bandwidth):
    if open < (avg - bandwidth):
        return open
                                                                     

# --- define parameters ---
invested_money = 1000
freq = 60 # data frequency in seconds
cost_per_trade = 1
perc_band = 1.0 # in %
hours_window = 10 # in hours
spread = 0.1 # spread in % (Differenz zwischen Kauf und Verkaufskurs)
avrg_type = 'mov_avrg'# mov_avrg or abs_avrg
save_output = True
# -------------------------

buy_val_list = []
buy_time_list = []
sell_val_list = []
sell_time_list = []
buy_val = None
sell_val = None

# len_window, time_delta = extract_window_length(hours=hours_window, data=raw_data)
len_window = int(3600*hours_window/freq)
data = get_data(len_window=len_window, freq=freq)

# todo: implement trailing stop for buy and sell orders
bandwidth = calc_bandwidth(percentage=perc_band, init_avg=data[avrg_type][len_window])
init_buy, buy_index = find_first_buy(data=data, bandwidth=bandwidth, len_window=len_window)
buy_val_list.append(init_buy + 0.5*spread*0.01*init_buy)
buy_time_list.append(data.axes[0][buy_index])
sell_flag = False
for i in range(buy_index, len(data)):
    sell_val = check_sell(open=data['open'][i], avg=data[avrg_type][i], buy_val=buy_val_list[-1], bandwidth=bandwidth)
    if sell_val is not None and sell_flag == False:
        sell_val_list.append(sell_val - 0.5*spread*0.01*sell_val) # correct values with spread
        sell_time_list.append(data.axes[0][i])
        sell_flag = True
    if sell_val_list:
        buy_val = check_buy(open=data['open'][i], avg=data[avrg_type][i], sell_val=sell_val_list[-1],
                            bandwidth=bandwidth)
    if buy_val is not None and sell_flag:
        buy_val_list.append(buy_val + 0.5*spread*0.01*buy_val)
        buy_time_list.append(data.axes[0][i])
        sell_flag = False

num_trades = len(buy_val_list) + len(sell_val_list)
sell_val_list = np.array(sell_val_list)
buy_val_list = np.array(buy_val_list)
win_trade_abs = sell_val_list - buy_val_list[0:len(sell_val_list)]
win_trade_perc = np.sum(win_trade_abs/sell_val_list)*100
abs_profit = invested_money*win_trade_perc*0.01 - num_trades*cost_per_trade

if save_output:
    delta = data.index.max() - data.index.min()
    time_delta = delta.total_seconds()
    file = open("Out-{}to{}.txt".format(start_date, end_date), "w")
    file.write('date: {} to {} \n absolute time [hours]: {} \n num_trades: {} \n win_trade_perc [without order cost]: {} \n invested_money: {}'
               ' \n abs_profit:{} \n \n \n perc_band: {} \n hours_window: {} \n spread: {} \n avrg_type: {}'
               .format(start_date, end_date, time_delta/60**2, num_trades, win_trade_perc, invested_money, abs_profit,
                       perc_band, hours_window, spread, avrg_type))
    file.close()
    plt.plot(data['open'], marker='o')
    plt.plot(data['mov_avrg'], marker='x')
    plt.plot(data['abs_avrg'], marker='x')
    plt.plot(buy_time_list, buy_val_list, marker='.', markersize=40, markerfacecolor='red', linestyle='None')
    plt.plot(sell_time_list, sell_val_list, marker='.', markersize=40, markerfacecolor='green', linestyle='None')
    plt.savefig('Fig-{}to{}.svg'.format(start_date, end_date), format='svg')

