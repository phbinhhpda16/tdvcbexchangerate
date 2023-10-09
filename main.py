from tvDatafeed import TvDatafeed, Interval
import pandas as pd
import datetime as dt
from bs4 import BeautifulSoup
from shareplum import Site
from shareplum import Office365
import requests

tv = TvDatafeed('', '')
today = dt.datetime.today().strftime('%d/%m/%Y')
yesterday = (dt.datetime.today() + dt.timedelta(days=-1)).strftime('%d/%m/%Y')

def data_extract(symbol, exchange):
    data = tv.get_hist(symbol=symbol,exchange=exchange,interval=Interval.in_daily,n_bars=1)
    data.reset_index(inplace= True)
    data.rename(columns={'datetime': "Update Day", "close": symbol}, inplace=True)
    data = data[["Update Day", symbol]]
    data["Update Day"] = data["Update Day"].dt.strftime('%d/%m/%Y')
    if data.iloc[0]["Update Day"] != today:
        data.at[0, "Update Day"] = today
    return data

def vcb(date):
    data_list = []
    date_string = date.strftime("%d/%m/%Y")
    update_day = date_string
    url = "https://portal.vietcombank.com.vn/Usercontrols/TVPortal.TyGia/pXML.aspx"
    proxies = {"http": "http://10.10.1.10:3128","https": "https://10.10.1.10:1080",}
    response = requests.get(url, proxies=proxies)
    html_content = response.content
    soup = BeautifulSoup(html_content, "xml")
    jpn = soup.find('Exrate', {'CurrencyCode': 'JPY'}).get('Sell')
    usd = soup.find('Exrate', {'CurrencyCode': 'USD'}).get('Sell')
    data_list.append([update_day, jpn, usd])
    data = pd.DataFrame(data_list, columns=["Update Day", "JPN", "USD"])
    return data

aks = data_extract('AKS1!', 'NYMEX')
usdjpn = data_extract('USDJPY', 'OANDA')
vcb_rate = vcb(dt.datetime.today())

all_data = vcb_rate.merge(aks, on = "Update Day", how = "outer")
all_data = all_data.merge(usdjpn, on = "Update Day", how = "outer")
all_data = all_data.to_dict("records")

#Add new data
authcookie = Office365('https://datapot01.sharepoint.com', username = 'exratekinkin@datapot01.onmicrosoft.com', password = '@Datapot2018').GetCookies()
site = Site('https://datapot01.sharepoint.com/sites/ExchangeRate', authcookie=authcookie)
sp_list = site.List("exrate")
#sp_list.UpdateListItems(data = all_data, kind = 'New')
print(all_data)

#Update yesterday data
sp_data = sp_list.GetListItems(fields=['ID', 'Title'])[-2]
sp_data_df = pd.DataFrame(sp_data, index=[0])
sp_data_df.rename(columns = {"Title": "Update Day"}, inplace = True)
aks_yesterday = aks
aks_yesterday.at[0, "Update Day"] = yesterday
sp_data_df = sp_data_df.merge(aks_yesterday, on = "Update Day", how = "outer")
yesterday_update = sp_data_df.to_dict("records")
#sp_list.UpdateListItems(data = yesterday_update, kind = 'Update')
print(yesterday_update)
