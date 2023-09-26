from tvDatafeed import TvDatafeed, Interval
import pandas as pd
import datetime as dt
import requests
from bs4 import BeautifulSoup
from shareplum import Site
from shareplum import Office365

tv = TvDatafeed('thuongdoan.bg@gmail.com', 'Kinkin@123')
today = dt.datetime.today().strftime('%d/%m/%Y')

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
    response = requests.get(url)
    html_content = response.content
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

authcookie = Office365('https://datapot01.sharepoint.com', username = 'exratekinkin@datapot01.onmicrosoft.com', password = '@Datapot2018').GetCookies()
site = Site('https://datapot01.sharepoint.com/sites/ExchangeRate', authcookie=authcookie)
sp_list = site.List("exrate")
sp_list.UpdateListItems(data = all_data, kind = 'New')

print(all_data)

#vcb = pd.read_csv("E:\\Code\\VCB\\VCB.csv")

#all_data = vcb.merge(aks, on = "Update Day", how = "outer")
#all_data = all_data.merge(usdjpn, on = "Update Day", how = "outer")
#all_data = all_data.fillna(method='ffill')

#print(all_data.head(20))

#result_path = "E:\\Code\\VCB\\VCB.xlsx"  
#sheet_result = 'Sheet2' 
#writer = pd.ExcelWriter(result_path, engine = 'xlsxwriter')
#all_data.to_excel(writer, sheet_name=sheet_result, index=False)
#writer.save()

#,'https://datapot01.sharepoint.com','exratekinkin@datapot01.onmicrosoft.com','@Datapot2018','https://datapot01.sharepoint.com/sites/ExchangeRate',"exchange_rate"
