import pandas as pd


class TestMovingAverage:

    def __init__(self, data, len_window_points, config):
        self.data = data
        self.len_window_points = len_window_points
        self.average_type = config['average_type']
        self.band_percentage = config['band_percentage']
        self.spread = config['spread']
        self.sell_values = None
        self.buy_values = None
        self.bandwidth = None

    def trade(self):
        self.buy_values, buy_idx = self.find_first_buy()

        # initial condition after first buy
        self.sell_values = pd.DataFrame()
        sell_flag = False

        for i in range(buy_idx, len(self.data)):

            # define band value range to ensure winning trades
            band_value = self.data['Open'][i] * self.band_percentage * 0.01

            # check sell conditions for every timestep
            sell_value = self.check_sell(timestep=i, bandwidth=band_value)
            if sell_value is not None and sell_flag is False:
                sell_value = sell_value * (1 - 0.5 * self.spread * 0.01)  # spread correction
                self.sell_values = self.sell_values.append(sell_value)
                sell_flag = True

            if sell_flag:
                buy_val = self.check_buy(timestep=i, bandwidth=band_value)
                if buy_val is not None:
                    buy_val = buy_val * (1 + 0.5 * self.spread * 0.01)  # spread correction
                    self.buy_values = self.buy_values.append(buy_val)
                    sell_flag = False

        return self.buy_values, self.sell_values

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
        if self.data['Open'].iloc[[timestep][0]] < self.data[self.average_type].iloc[[timestep][0]] - bandwidth :
            return self.data[['Open']].iloc[[timestep]]
        else:
            return None
