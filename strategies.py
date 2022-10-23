import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import strategy_handler


class TestMovingAverage(strategy_handler.TestStrategy):
    """
    This class defines a moving average approach with a performance band to evaluate trading decisions
    """

    def __init__(self, config, data, len_window_points):
        super().__init__(data, config)
        self.average_type = config['average_type']
        self.desired_win = config['desired_win']
        self.len_window_points = len_window_points

        self.order_cost_perc = self.cost_trade if self.cost_trade_measure == 'perc' \
            else (self.cost_trade / self.invested_money) * 100
        self.band_values = None

    def trade(self):
        # set initial conditions for first buy
        self.buy_values, buy_idx = self.find_first_buy()
        real_first_buy = self.buy_values * (1 - 0.5 * self.spread * 0.01 - self.order_cost_perc * 0.01)
        self.real_buy_values = pd.concat([self.real_buy_values, real_first_buy])
        buy_flag = True  # True if last trade was buy

        # define band value range to ensure trade with desired win
        self.band_values = self.calc_bandwidth()

        for i in range(self.len_window_points - 1, len(self.data)):
            if i >= buy_idx:  # start looking for selling points after first buy
                if buy_flag:  # last trade was a buy-order
                    sell_value = self.check_sell(timestep=i, bandwidth=self.band_values[self.buy_values.index[-1]]) # refer to the last buy band value
                    if sell_value is not None:
                        self.sell_values = pd.concat([self.sell_values, sell_value])
                        real_sell = sell_value * (1 - 0.5 * self.spread * 0.01 - self.order_cost_perc * 0.01)
                        self.real_sell_values = pd.concat([self.real_sell_values, real_sell])
                        buy_flag = False
                else:  # last trade was a sell-order
                    buy_value = self.check_buy(timestep=i, bandwidth=self.band_values[i])
                    if buy_value is not None:
                        self.buy_values = pd.concat([self.buy_values, buy_value])
                        real_buy = buy_value * (1 + 0.5 * self.spread * 0.01 + self.order_cost_perc * 0.01)
                        self.real_buy_values = pd.concat([self.real_buy_values, real_buy])
                        buy_flag = True

        if self.real_sell_values.empty:
            raise ValueError('Found no point to sell.')

    def calc_bandwidth(self):
        # no band values before window movement
        band_values = pd.DataFrame([np.nan] * (self.len_window_points - 1))
        band_values.index = self.data.index[:(self.len_window_points - 1)]
        for k in range(self.len_window_points - 1, len(self.data)):
            band_value = pd.DataFrame(self.data[self.average_type][[k]] * 0.01 * (0.5 * self.desired_win
                                                                                  + 0.5 * self.spread
                                                                                  + 0.5 * self.order_cost_perc))
            band_values = pd.concat([band_values, band_value], axis=0)
        return band_values[self.average_type]

    def find_first_buy(self):
        first_buy = None
        for i in range(self.len_window_points, len(self.data)):
            if self.data['Open'][i] < (
                    self.data[self.average_type][i] - self.data['Open'][i] * 0.01 * (0.5 * self.desired_win
                                                                                     + 0.5 * self.spread
                                                                                     + 0.5 * self.order_cost_perc)):
                first_buy = self.data.iloc[[i]]
                return first_buy[['Open']], i
        if first_buy is None:
            raise ValueError('Found no first buy point.')

    def check_sell(self, timestep, bandwidth):
        if (self.data['Open'].iloc[[timestep][0]]) > (self.real_buy_values['Open'].iloc[[-1][0]] + (2 * bandwidth)):
            return self.data[['Open']].iloc[[timestep]]
        else:
            return None

    def check_buy(self, timestep, bandwidth):
        if self.data['Open'].iloc[[timestep][0]] < self.data[self.average_type].iloc[[timestep][0]] - bandwidth:
            return self.data[['Open']].iloc[[timestep]]
        else:
            return None

    def save_results(self):
        super().save_results()

        fig, ax = plt.subplots()
        ax.plot(self.data['Open'], marker='x', markersize=10, label='Stock Data')
        ax.plot(self.data['moving_mean'], marker='x', markersize=10, color='tab:orange', label='Stock Data Moving Mean')
        ax.plot(self.data['absolut_mean'], color='tab:gray', label='Stock Data Absolut Mean')
        ax.fill_between(self.data['moving_mean'].index, self.data['moving_mean'],
                        self.data['moving_mean'] - self.band_values, color='tab:orange', alpha=.5, label='Band')
        ax.plot(self.buy_values, marker='.', markersize=20, markeredgecolor='r', markerfacecolor='r', alpha=.5,
                linestyle='None', label='Buy Value (incl. Trading Cost & Spread)')
        ax.plot(self.sell_values, marker='.', markersize=20, markeredgecolor='g', markerfacecolor='g', alpha=.5,
                linestyle='None', label='Sell Value (incl. Trading Cost & Spread)')
        ax.legend()
        plt.savefig(r'./{}/plot_{}.svg'.format(self.tradingbot_name, self.tradingbot_name), format='svg')
