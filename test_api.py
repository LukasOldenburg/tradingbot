from polygon import RESTClient
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt

matplotlib.use('TkAgg')

client = RESTClient(api_key="UorxHXe7kpzpGLyWGQyiK8U54iXSyqGn")

ticker = "ACWI"
time_zone = 'EST'

# List Aggregates (Bars)
bars = client.get_aggs(ticker=ticker, multiplier=1, timespan="minute", from_="2022-01-03", to="2022-07-01", limit=50000)

data = pd.DataFrame()
for bar in bars:
    data = pd.concat(
        (data, pd.DataFrame(data={'timestamp': [pd.Timestamp(ts_input=bar.timestamp, unit='ms', tz=time_zone)],
                                  'open': [bar.open],
                                  'close': [bar.close],
                                  }
                            )
         ))
    # data.insert('timestamp': pd.Timestamp(ts_input=bar.timestamp, unit='ms', tz=time_zone))

fig, ax = plt.subplots()
ax.plot(data['timestamp'], data['open'], marker='x', markersize=10, label='Stock Data')
fig.show()
A = 1
