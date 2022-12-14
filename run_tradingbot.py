import yaml
from tradingbot import TradingBot
import matplotlib
matplotlib.rcParams['backend'] = 'TkAgg'
matplotlib.rc('figure', figsize=(20,15))

file_name = 'config.yaml'
with open(file_name, 'r') as f:
    config = yaml.safe_load(f)

Bot = TradingBot(config=config)
Bot.test()

