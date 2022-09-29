import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


class TestStrategy:

    """
    This is a parent class for all strategies
    """

    def __init__(self, data, config):
        self.data = data
        self.invested_money = config['invested_money']
        self.tradingbot_name = config['tradingbot_name']
        self.save_results = config['save_results']
        self.spread = config['spread']
        self.perc_profit = None
        self.abs_profit = None
        self.trade_wins_perc = None
        self.num_trades = None
        self.buy_values = None
        self.sell_values = None

        if config['cost_trade_abs'] is None and isinstance(config['cost_trade_perc'], float):
            self.cost_trade_measure = 'perc'
            self.cost_trade = config['cost_trade_perc']
        elif config['cost_trade_perc'] is None and isinstance(config['cost_trade_abs'], float):
            self.cost_trade_measure = 'abs'
            self.cost_trade = config['cost_trade_abs']
        else:
            raise ValueError('Check values for cost_trade_abs and cost_trade_perc in yaml file.')

    def evaluate(self):
        buy_val = np.squeeze(np.array(self.buy_values))
        sell_val = np.squeeze(np.array(self.sell_values))
        self.num_trades = np.size(buy_val) + np.size(sell_val)

        # calculate wins deducted by trading costs
        # todo check if conditions here. only if buy_val bigger than sell_val
        if self.cost_trade_measure == 'perc' and sell_val.size != 0:
            self.trade_wins_perc = (sell_val / buy_val[0:np.size(sell_val)] - 1) - self.cost_trade * 0.01
        elif self.cost_trade_measure == 'abs' and sell_val.size != 0:
            #todo check if this is valid
            self.trade_wins_perc = (sell_val / (buy_val[0:np.size(sell_val)] + self.cost_trade * 0.01 * sell_val)) - 1
        else:
            raise ValueError('Bot was not able to find a point to sell.')

        self.abs_profit = np.sum(self.invested_money * self.trade_wins_perc)
        self.perc_profit = (self.abs_profit / self.invested_money) * 100

        return self.num_trades, self.trade_wins_perc, self.abs_profit, self.perc_profit

    def plot_results(self):
        if self.save_results:
            file = open("out_{}.txt".format(self.tradingbot_name), "w")
            file.write('start_date: {} \n end_date: {} \n trading time: {} \n invested_money: {} \n\n\n num_trades: {}'
                       '\n perc_profit: {} \n abs_profit: {}'
                       .format(self.data.index[0], self.data.index[-1], self.data.index[-1] - self.data.index[0],
                               self.invested_money, self.num_trades, self.perc_profit, self.abs_profit))
            file.close()


class TestMovingAverage(TestStrategy):

    """
    This class defines a moving average approach with a performance band to evaluate trading decisions
    """

    def __init__(self, config, data, len_window_points):
        super().__init__(data, config)
        self.average_type = config['average_type']
        self.band_percentage = config['band_percentage']
        self.len_window_points = len_window_points
        self.band_values = np.empty(self.len_window_points - 1)
        self.band_values.fill(np.nan)

    def trade(self):
        self.buy_values, buy_idx = self.find_first_buy()

        # initial condition after first buy
        self.sell_values = pd.DataFrame()
        sell_flag = False

        for i in range(self.len_window_points - 1, len(self.data)):

            # define band value range to ensure winning trades
            band_value = self.data[self.average_type][i] * self.band_percentage * 0.01
            self.band_values = np.append(self.band_values, band_value)

            if i >= buy_idx:  # start looking for selling points after first buy
                sell_value = self.check_sell(timestep=i, bandwidth=band_value)
                if sell_value is not None and sell_flag is False:
                    sell_value = sell_value * (1 - 0.5 * self.spread * 0.01)  # spread correction
                    self.sell_values = pd.concat([self.sell_values, sell_value])
                    sell_flag = True

                if sell_flag:
                    buy_value = self.check_buy(timestep=i, bandwidth=band_value)
                    if buy_value is not None:
                        buy_value = buy_value * (1 + 0.5 * self.spread * 0.01)  # spread correction
                        self.buy_values = pd.concat([self.buy_values, buy_value])
                        sell_flag = False

    def find_first_buy(self):
        first_buy = None
        for i in range(self.len_window_points, len(self.data)):
            if self.data['Open'][i] < (
                    self.data[self.average_type][i] - self.data['Open'][i] * self.band_percentage * 0.01):
                first_buy = self.data.iloc[[i]]
                return first_buy[['Open']], i
        if first_buy is None:
            raise ValueError('Found no first buy point.')

    def check_sell(self, timestep, bandwidth):
        cond1 = self.data['Open'].iloc[[timestep][0]] > self.buy_values['Open'].iloc[[-1][0]] + bandwidth
        cond2 = self.data['Open'].iloc[[timestep][0]] > self.data[self.average_type].iloc[[timestep][0]] + bandwidth
        if cond1 and cond2:
            return self.data[['Open']].iloc[[timestep]]
        else:
            return None

    def check_buy(self, timestep, bandwidth):
        # todo implement strategy to not buy higher than entry price
        if self.data['Open'].iloc[[timestep][0]] < self.data[self.average_type].iloc[[timestep][0]] - bandwidth:
            return self.data[['Open']].iloc[[timestep]]
        else:
            return None

    def plot_results(self):
        super().plot_results()

        # todo visualize buy/sell point with and without order cost/spread
        upper_band = self.data['moving_mean'] + self.band_values
        lower_band = self.data['moving_mean'] - self.band_values

        fig, ax = plt.subplots()
        ax.plot(self.data['Open'], marker='x', markersize=2, label='Stock Data')
        ax.plot(self.data['moving_mean'], marker='x', markersize=2, color='tab:orange', label='Stock Data Moving Mean')
        ax.plot(self.data['absolut_mean'], color='tab:gray', label='Stock Data Absolut Mean')
        ax.fill_between(upper_band.index, upper_band, lower_band, color='tab:orange', alpha=.5, label='Band')
        ax.plot(self.buy_values, marker='.', markersize=20, markeredgecolor='r', markerfacecolor='r', linestyle='None',
                label='Buy Value (incl. Trading Cost & Spread)')
        ax.plot(self.sell_values, marker='.', markersize=20, markeredgecolor='g', markerfacecolor='g',
                linestyle='None', label='Sell Value (incl. Trading Cost & Spread)')
        ax.legend()
        plt.savefig('plot_{}.svg'.format(self.tradingbot_name), format='svg')
