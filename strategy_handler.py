import numpy as np
import pandas as pd


class TestStrategy:
    """
    This is a parent class for all strategies
    """

    def __init__(self, data, config):
        self.data = data
        self.invested_money = config['invested_money']
        self.tradingbot_name = config['tradingbot_name']
        self.save_outcome = config['save_outcome']
        self.spread = config['spread']
        self.sell_values = pd.DataFrame()
        self.real_sell_values = pd.DataFrame()
        self.real_buy_values = pd.DataFrame()
        self.buy_values = None
        self.num_trades = None
        self.perc_profit_long = None
        self.perc_profit_bot = None
        self.accounting_value = None
        self.strategy_profit = None

        if config['cost_trade_abs'] is None and isinstance(config['cost_trade_perc'], float):
            self.cost_trade_measure = 'perc'
            self.cost_trade = config['cost_trade_perc']
        elif config['cost_trade_perc'] is None and isinstance(config['cost_trade_abs'], float):
            self.cost_trade_measure = 'abs'
            self.cost_trade = config['cost_trade_abs']
        else:
            raise ValueError('Check values for cost_trade_abs and cost_trade_perc in yaml file.')

    def evaluate(self):
        real_buy_val = np.squeeze(np.array(self.real_buy_values))
        real_sell_val = np.squeeze(np.array(self.real_sell_values))
        self.num_trades = np.size(real_buy_val) + np.size(real_sell_val)
        if np.size(real_sell_val) == np.size(real_buy_val):
            self.strategy_profit = (np.sum((real_sell_val / real_buy_val) - 1)) * 100
            self.accounting_value = 0.0
        else:
            self.strategy_profit = (np.sum((real_sell_val / real_buy_val[:-1]) - 1)) * 100
            strategy_profit_per_trade = ((real_sell_val / real_buy_val[:-1]) - 1) * 100
            self.accounting_value = ((self.data['Open'][-1] / real_buy_val[-1]) - 1) * 100
        self.perc_profit_bot = (self.strategy_profit + self.accounting_value)
        self.perc_profit_long = ((self.data['Open'][-1] / real_buy_val[0]) - 1) * 100

    def save_results(self):
        if self.save_results:
            file = open("out_{}.txt".format(self.tradingbot_name), "w")
            file.write('tradingbot_name: {}\n\nstart_date: {}\nend_date: {}\ntrading time: {}\ninvested_money: {}\n '
                       '\n\n##### BOT-STATS #####\nnum_trades: {}\nstrategy_profit [%]: {}\naccounting_value [%]: {}\n'
                       'perc_profit_bot: {}\n\n##### COMPARISON #####\nperc_profit_long: {}'
                       .format(self.tradingbot_name, self.data.index[0], self.data.index[-1],
                               self.data.index[-1] - self.data.index[0], self.invested_money, self.num_trades,
                               self.strategy_profit, self.accounting_value, self.perc_profit_bot, self.perc_profit_long))
            file.close()
