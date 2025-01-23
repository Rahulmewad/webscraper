import requests
import datetime
from bs4 import BeautifulSoup
import pandas as pd

cookies = {
    'test': 'money_back_guarantee',
    'first_visit_url': 'https://webscraper.io/test-sites/e-commerce/allinone',
    '_gcl_au': '1.1.239252677.1737461124',
    '_ga_Q9KY1T6XJQ': 'GS1.1.1737461124.1.0.1737461127.57.0.0',
    '_ga': 'GA1.1.1037102203.1737461124',
}

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:134.0) Gecko/20100101 Firefox/134.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    # 'Accept-Encoding': 'gzip, deflate, br, zstd',
    'DNT': '1',
    'Sec-GPC': '1',
    'Connection': 'keep-alive',
    # 'Cookie': 'test=money_back_guarantee; first_visit_url=https://webscraper.io/test-sites/e-commerce/allinone; _gcl_au=1.1.239252677.1737461124; _ga_Q9KY1T6XJQ=GS1.1.1737461124.1.0.1737461127.57.0.0; _ga=GA1.1.1037102203.1737461124',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Priority': 'u=0, i',
}

response = requests.get('https://webscraper.io/test-sites/e-commerce/allinone',headers=headers)

soup = BeautifulSoup(response.text,"html.parser")
pro_list = soup.find(attrs={'class':'col-lg-9'}).findAll(attrs={'class':'col-md-4 col-xl-4 col-lg-4'})

data_list = []
for item in pro_list:
    data_dict = {}
    title = item.find(attrs={'class':'title'}).text.strip()
    data_dict["Title"] = title
    
    price = item.find(attrs={'class':'price'}).text.strip()
    data_dict["Price"] = price
    
    review = item.find(attrs={'class':'review-count'}).text.strip()
    data_dict["Review"] = review
    
    data_list.append(data_dict)
    


df = pd.DataFrame(data_list)
data_time = str(datetime.datetime.now()).replace("-","_").replace(":","_").replace(".","_").replace(" ","_")
df.to_csv(f"web_data_{data_time}.csv",index=False)
print("Script Done")