import requests
from bs4 import BeautifulSoup
from google.cloud import translate_v2 as translate
from lxml import html,etree
import json
import pandas as pd

cookies = {
    'at_lp_exp': 'active=0&page=/jp/jp',
    'ni_d': 'C921148F-B907-4BBE-a448-DED20951A2ED',
    'anonymousId': '8F7335210B29D1FE7A5DD993498F679E',
    '_gcl_au': '1.1.764536520.1733920969',
    '_fbp': 'fb.1.1733920968656.527409830387',
    '_rdt_uuid': '1733920968657.c1b09054-03cd-4d02-93ab-55203b2a8794',
    'CONSUMERCHOICE_SESSION': 't',
    'rmStore': 'atm:pixel',
    'FPID': 'FPID2.2.tag6J2vo1Q5CBhG3zDy2PYT4kf8Fb9bXJoRtfPf2Vi4%3D.1733920969',
    'FPAU': '1.1.764536520.1733920969',
    '_pin_unauth': 'dWlkPVkyWmpOemczTURJdE1ERTJNeTAwWXpRM0xUZ3lOREF0TldKak5qVTBaRE15WkRNeg',
    's_ecid': 'MCMID%7C17773789350567797972319392627895238166',
    'AMCV_F0935E09512D2C270A490D4D%40AdobeOrg': '1994364360%7CMCMID%7C17773789350567797972319392627895238166%7CMCAID%7CNONE%7CMCOPTOUT-1733928188s%7CNONE%7CvVersion%7C3.4.0',
    'EU_COOKIE_LAW_CONSENT': 'true',
    'EU_COOKIE_LAW_CONSENT_legacy': 'true',
    'styliticsWidgetSession': '4469ac06-f997-49ce-a566-4aaa4819e908',
    'bluecoreNV': 'false',
    'forterToken': '0a2e534e76fc45ca9a222f7b857a8a40_1734021260906__UDF43-m4_13ck_7ubGrSp1gys%3D-124-v2',
    'RT': '"z=1&dm=nike.com&si=4a2189a6-00a6-4d66-ae81-efb9ae581cc1&ss=m4lkkox3&sl=0&tt=0"',
    'bc_nike_vietnam_triggermail': '%7B%22distinct_id%22%3A%20%22193b5be4f20870-0410f09f1592f5-26011851-100200-193b5be4f21da0%22%2C%22bc_persist_updated%22%3A%201734021242430%2C%22last_carted_product%22%3A%20%221015586730%22%7D',
    '_ga_VZJN08LNK6': 'GS1.1.1734358481.10.1.1734358481.60.0.0',
    'FPLC': 'JlxzoMxs1en7PbIq6bGaq1t9K%2FJoI9eTHHWqFOzh8u%2FQxmV1s3Nu1GHYrb%2F5D1WWabXxKXhzV61Abf2%2BwK8rZkKeDd%2FKGCQ5BSRu%2BX%2B66eiUMgjaCGnSmtSKNlL6kw%3D%3D',
    'geoloc': 'cc=IN,rc=MH,tp=vhigh,tz=GMT+5.50,la=18.98,lo=72.83',
    'ak_bmsc': 'E2750B5030FBB3F1C41F0849DB995DDD~000000000000000000000000000000~YAAQRXMsMWz9M7STAQAALFi20xrCV6KAV3Ld4Qq8WCykdmJQrFD5VE5egUIg5NQg3Tj1pPAGfRsanJhm8YB8hZA5O+Ya8JOdq3FjxrKeoa1D62KRRIQAcaZGANR2e9DmliLaHwepQOY3+aH3udEdNM+QQS17mFbklYNlqNlTcza7lonsnKzpffDie+8JOTTcBhr8xdi0sA8QPFjIOONAbTaVgfwn3pVWh0HoyRNQlAWucdRhVFL8AJ3FOIh7uiL/3NqF3efdngZRDSlbLX3eUHrlRS3aEbkoyem+Kad31pAL00u3Y2eaet35n9I6mfE249A0WDf7/R3bJkMboQTGyciSWWw3r+EXFKmel7CfPObvwBfOZ90qZXKijL9w9DNYUuSl6uPjhF0=',
    'at_check': 'true',
    'AKA_A2': 'A',
    'ni_cs': 'fdd3f991-3d93-4b62-991d-192510018771',
    '_gid': 'GA1.2.145414083.1734423764',
    '_clck': '110sfxu%7C2%7Cfrs%7C0%7C1812',
    'NIKE_COMMERCE_COUNTRY': 'JP',
    'NIKE_COMMERCE_LANG_LOCALE': 'ja_JP',
    'nike_locale': 'jp/ja_jp',
    'CONSUMERCHOICE': 'jp/ja_jp',
    'kndctr_F0935E09512D2C270A490D4D_AdobeOrg_cluster': 'ind1',
    'kndctr_F0935E09512D2C270A490D4D_AdobeOrg_identity': 'CiYxNzc3Mzc4OTM1MDU2Nzc5Nzk3MjMxOTM5MjYyNzg5NTIzODE2NlITCISZ%2Da27MhABGAEqBElORDEwAPAB67Ddnb0y',
    'mboxEdgeCluster': '41',
    'ppd': 'pdp|nikecom>pdp>%E3%83%8A%E3%82%A4%E3%82%AD%20%E3%82%A8%E3%82%A2%20%E3%83%9E%E3%83%83%E3%82%AF%E3%82%B9%20%E3%83%97%E3%83%A9%E3%82%B9%20%E3%83%89%E3%83%AA%E3%83%95%E3%83%88',
    'bluecore_pdp_view': 'true',
    'TTSVID': '1653ef50-c333-435b-b267-430b88e235f0',
    'pixlee_analytics_cookie_legacy': '%7B%22CURRENT_PIXLEE_USER_ID%22%3A%22f6303469-3583-d2a3-198a-fe4143ecb3c3%22%2C%22TIME_SPENT%22%3A109%2C%22BOUNCED%22%3Afalse%7D',
    'mbox': 'session%233b4fe01883c34eadbbc522a445d1cf78%231734426390%7CPC%233b4fe01883c34eadbbc522a445d1cf78%2E41%5F0%231797668598',
    'bc_nike_japan_triggermail': '%7B%22distinct_id%22%3A%20%22193b5be4f20870-0410f09f1592f5-26011851-100200-193b5be4f21da0%22%2C%22bc_persist_updated%22%3A%201734423828963%2C%22last_carted_product%22%3A%20%221015586730%22%7D',
    'bc_invalidateUrlCache_targeting': '1734424529597',
    '_ga_QTVTHYLBQS': 'GS1.1.1734423764.11.1.1734424530.0.0.1403588744',
    '_ga_EPVVRCQCFR': 'GS1.1.1734423764.1.1.1734424530.0.0.0',
    '_ga': 'GA1.2.712708.1733920969',
    'bm_sv': 'AE1B3C53F49E5CD4723B7FC3C439E397~YAAQLrcsMWfOTbeTAQAAMxTC0xoe3ws0ZXAjc4QKj+YNl8ndeNuVoO+MD3UDLySIPPCKScur0cfsbncI0gRST+HilqJ26+l/yU+pFFTz8X/t0auGXg0Y9Ju9dYTReGVF/3vZ/w4jshU2rhu2klKdDZ2eLkBsWfcaL9uFsw0VvrOcRrfPKSiDQfVsFWnm38ikjXbgcx645QvhUab6kiOS3vFRUsNwNMZ6Ip74kjoFdMSA2ODAYY0iiUFs4tdwH38=~1',
    'FPGSID': '1.1734423766.1734424531.G-QTVTHYLBQS.WF8VvtB0K38qipoprjrhLA',
    '_uetsid': '17c31d10bc5011efa9f4074811d8458e',
    '_uetvid': '6eda2760b7bd11ef9c54ed3fa58ae034',
    '_clsk': '1x044ci%7C1734424533084%7C4%7C1%7Cb.clarity.ms%2Fcollect',
    'RT': '"z=1&dm=www.nike.com&si=4a2189a6-00a6-4d66-ae81-efb9ae581cc1&ss=m4lkkox3&sl=1&tt=lv4&rl=1"',
}
import requests
headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-US,en;q=0.9',
    'cache-control': 'max-age=0',
    'if-none-match': '"519d7-mK8W8yelX80t+Cqm4HgfK4ZUVk0"',
    'priority': 'u=0, i',
    'referer': 'https://www.nike.com/jp/w?q=nike&vst=nike',
    'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
    'sec-ch-ua-full-version-list': '"Google Chrome";v="131.0.6778.140", "Chromium";v="131.0.6778.140", "Not_A Brand";v="24.0.0.0"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-model': '""',
    'sec-ch-ua-platform': '"Windows"',
    'sec-ch-ua-platform-version': '"10.0.0"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
}


url = 'https://www.nike.com/jp/t/%E3%83%8A%E3%82%A4%E3%82%AD-%E3%82%A8%E3%82%A2-%E3%83%9E%E3%83%83%E3%82%AF%E3%82%B9-2013-%E3%82%B8%E3%83%A5%E3%83%8B%E3%82%A2%E3%82%B7%E3%83%A5%E3%83%BC%E3%82%BA-tb1PDp/555426-100'
page_source = requests.get(url,headers=headers)
html_contain = html.fromstring(page_source.content)

image =  [img for img in html_contain.xpath("//div[contains(@class,'grid-item') and contains(@class, 'product-imagery')]//div[@data-testid='HeroImgContainer']//img/@src")]
images = "; ".join(image)
print(images)

picture_cnt = len(image)
print(picture_cnt)

json_data_script = html_contain.xpath("//script[@id='__NEXT_DATA__']//text()")[0]
json_data = json.loads(json_data_script)
json_data_list = json_data['props']['pageProps']['productGroups'][0]['products']

    
for key_data,values_data in json_data_list.items():
    print('-----------------------------------')
    sku_id = key_data
    print(sku_id)
    company_name = values_data['brands'][0]
    print(company_name)
    
    retailer_id = values_data['productInfo']['title']
    print(retailer_id)
    
    ip_in_vat = values_data['prices']['currentPrice']
    print(ip_in_vat)
    if float(ip_in_vat)<15000:
        print('shipp :  ',550)

    min_cp = values_data['prices']['currentPrice']
    print(min_cp)
    
    site_url = values_data['pdpUrl']['url']
    print(site_url)
    
    product_desc = values_data['productInfo']['productDescription'].strip()
    print(product_desc)
    
    retailer_group_artical = key_data
    print(retailer_group_artical)
    
    color_group = values_data['colorDescription']
    print(color_group)
    
    retailer_model_id = values_data['styleCode']
    print(retailer_model_id)
    
    styleCode = values_data['styleCode']
    review_url = "https://api.nike.com/products/experience/v1/d9a5bc42-4b9c-4976-858a-f159cf99c647/VN/en-GB/styleCode/{}?count=3"
    review_url = review_url.format(styleCode)
    print(review_url)
    review_source = requests.get(review_url,headers=headers)
    review_json = json.loads(review_source.text)
    
    cunsumer_rating_avg = review_json['ratingsAndReviews']['averageOverallRating']
    print(cunsumer_rating_avg)

    cunsumer_rating_cnt = review_json['ratingsAndReviews']['totalReviews']
    print(cunsumer_rating_cnt)

    
    
    
