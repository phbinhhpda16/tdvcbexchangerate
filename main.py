from tvDatafeed import TvDatafeed, Interval
import pandas as pd
import datetime as dt
from bs4 import BeautifulSoup
from shareplum import Site
from shareplum import Office365
import requests
import urllib3
import ssl


class CustomHttpAdapter (requests.adapters.HTTPAdapter):
    # "Transport adapter" that allows us to use custom ssl_context.
    def __init__(self, ssl_context=None, **kwargs):
        self.ssl_context = ssl_context
        super().__init__(**kwargs)

    def init_poolmanager(self, connections, maxsize, block=False):
        self.poolmanager = urllib3.poolmanager.PoolManager(
            num_pools=connections, maxsize=maxsize,
            block=block, ssl_context=self.ssl_context)

def get_legacy_session():
    ctx = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    ctx.options |= 0x4  # OP_LEGACY_SERVER_CONNECT
    session = requests.session()
    session.mount('https://', CustomHttpAdapter(ctx))
    return session

tv = TvDatafeed('thuongdoan.bg@gmail.com', 'Kinkin@123')
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
    url = "https://portal.vietcombank.com.vn/UserControls/TVPortal.TyGia/pListTyGia.aspx?txttungay={}&BacrhID=1&isEn=False".format(date_string)

    request = get_legacy_session().get(url)
    html_content = request.content
    soup = BeautifulSoup(html_content, "html.parser")
    try:
        table = soup.find("table", class_="tbl-01 rateTable")
        rows = table.find_all("tr")
        for row in rows:
            cells = row.find_all("td")
            if len(cells) == 5:  
                currency_code = cells[1].text.strip()
                sell_rate = cells[4].text.strip()
                update_day = date_string
                if currency_code == "JPY":
                    jpn = sell_rate
                elif currency_code == "USD":
                    usd = sell_rate
        data_list.append([update_day, jpn, usd])
    except:
        print(date_string)
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
print(sp_list)

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
