import strategies
import yfinance as yf


class TradingBot:

    """
    This class can test a Trading Bot with a specified trading strategy
    """

    def __init__(self, config):

        self.config = config
        self.tradingbot_category = config['tradingbot_category']
        self.stock_name = config['stock_name']
        self.start_date = config['start_date']
        self.end_date = config['end_date']
        self.frequency = config['frequency']
        self.window_len = config['window_len']
        self.data = None
        self.window_len_points = None
        self.strategy = None

    def test(self):
        # get test stock data and extract necessary information during preprocessing
        self.data = self.get_test_data()
        self.data, self.window_len_points = self.preprocess_test_data(self.data, self.window_len)

        # select strategy type
        if self.tradingbot_category == 'mean':
            self.strategy = strategies.TestMovingAverage(data=self.data, config=self.config,
                                                         len_window_points=self.window_len_points)

        else:
            raise Exception('No strategy found with name {}'.format(self.tradingbot_category))

        # start trading
        self.strategy.trade()

        # evaluate, plot and save results
        self.strategy.evaluate()
        self.strategy.plot_results()

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

    def get_test_data(self):
        data = yf.download(tickers=self.stock_name, start=self.start_date, end=self.end_date, interval=self.frequency)
        return data
