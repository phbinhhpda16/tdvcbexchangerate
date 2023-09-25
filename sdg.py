from tvDatafeed import TvDatafeed, Interval

tv = TvDatafeed('', '')

nifty_index_data = tv.get_hist(symbol='AKS1!',exchange='NYMEX',interval=Interval.in_daily,n_bars=5000)

print(nifty_index_data["close"])
