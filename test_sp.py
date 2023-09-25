from shareplum import Site
from shareplum import Office365
import datetime

authcookie = Office365('https://datapot01.sharepoint.com', username='binhph@datapot01.onmicrosoft.com', password='@1L0v3900').GetCookies()
site = Site('https://datapot01.sharepoint.com/sites/Bnh', authcookie=authcookie)
sp_list = site.List('Test')

my_data = data=[{'Title': 'First Row!', 'Họ và tên': datetime.datetime.now()}]
sp_list.UpdateListItems(data=my_data, kind='New')

print(data)