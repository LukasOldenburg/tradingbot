import strategies
import utils


class TradingBot:
    """
    The class TestStrategy tests a specified strategy with historical stock data.

    Parameters
    ----------
    :param strategy_name

    """

    # todo finish docstring

    def __init__(self, config):

        self.config = config
        self.strategy_name = config['strategy_name']
        self.stock_name = config['stock_name']
        self.start_date = config['start_date']
        self.end_date = config['end_date']
        self.frequency = config['frequency']
        self.window_len = config['window_len']
        self.data = None
        self.window_len_points = None
        self.strategy = None
        self.buy_values = None
        self.sell_values = None

    def test(self):
        # get test stock data and extract necessary information during preprocessing
        self.data = utils.get_test_data(stock_name=self.stock_name, start_date=self.start_date, end_date=self.end_date,
                                        frequency=self.frequency)
        self.data, self.window_len_points = self.preprocess_test_data(self.data, self.window_len)

        # select strategy type
        if self.strategy_name == 'adapted_mean':
            self.strategy = strategies.TestMovingAverage(data=self.data, len_window_points=self.window_len_points,
                                                         config=self.config)

        else:
            raise Exception('No strategy found with name {}'.format(self.strategy_name))

        self.buy_values, self.sell_values = self.strategy.trade()

        return self.buy_values, self.sell_values, self.data

    def preprocess_test_data(self, data, window_len):
        if self.frequency == '1m':
            length = window_len * 60
        elif self.frequency == '1d':
            length = window_len
        else:
            raise ValueError('No valid frequency value')
        data['moving_mean'] = data['Open'].rolling(length).mean()
        data['absolut_mean'] = data['Open'].mean()
        return data, length
