import yfinance as yf


def get_test_data(stock_name='EUNL.DE', start_date='2012-09-20', end_date='2022-09-27', frequency='1d'):
    data = yf.download(tickers=stock_name, start=start_date, end=end_date, interval=frequency)
    return data
