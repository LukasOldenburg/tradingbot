import yaml
from tradingbot import TradingBot
import matplotlib
import matplotlib.pyplot as plt

matplotlib.rcParams['backend'] = 'TkAgg'

file_name = 'config.yaml'
with open(file_name, 'r') as f:
    config = yaml.safe_load(f)

Bot = TradingBot(config=config)
buy_values, sell_values, data = Bot.test()

A=1

plt.plot(data['Open'])
plt.plot(data['moving_mean'])
plt.plot(buy_values, marker='x', markersize=20, markeredgecolor='r', linestyle='None')
plt.plot(sell_values, marker='x', markersize=20, markeredgecolor='g', linestyle='None')