from tvDatafeed import TvDatafeed, Interval
from shareplum import Site
from shareplum import Office365

tv = TvDatafeed('thuongdoan.bg@gmail.com', 'Kinkin@123')

def data_extract(symbol, exchange,sp_site,user_name,password,site_url,list):
    data = tv.get_hist(symbol=symbol,exchange=exchange,interval=Interval.in_daily,n_bars=1)
    data.reset_index(inplace= True)
    data.rename(columns={'datetime': 'Title'}, inplace=True)
    data = data[["Title", "close"]]
    data_dict = data.to_dict(orient = 'records')
    authcookie = Office365(sp_site, username=user_name, password=password).GetCookies()
    site = Site(site_url, authcookie=authcookie)
    sp_list = site.List(list)
    sp_list.UpdateListItems(data=data_dict, kind='New')
    print("Done!")

data_extract('AKS1!', 'NYMEX','https://datapot01.sharepoint.com','binhph@datapot01.onmicrosoft.com','@1L0v3900','https://datapot01.sharepoint.com/sites/Test',"sdg")
data_extract('USDJPY', 'OANDA','https://datapot01.sharepoint.com','binhph@datapot01.onmicrosoft.com','@1L0v3900','https://datapot01.sharepoint.com/sites/Test',"usdjpn")


