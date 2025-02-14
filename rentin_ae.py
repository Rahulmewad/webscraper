# Scrape property site data 


import requests
import json
from bs4 import BeautifulSoup
from lxml import html
import sys
import pandas as pd
from lxml import html,etree
import json


def property_type_get(page_html):
    property_type = "-"
    try:
        property_type = page_html.xpath("//ul[@class='breadcrumbs']//li//a//span//text()")[-2]
    except Exception as e:
        line_no = sys.exc_info()[-1].tb_lineno
        error_desc = f"Exception occured in property_type_get : {line_no} -- {e}"
        print(error_desc)
    return property_type

def property_name_or_title_get(page_html):
    property_name_or_title = "-"
    try:
        property_name_or_title = page_html.xpath("//div[@class='title']//h1[@class='heading']//text()")[0]
    except Exception as e:
        line_no = sys.exc_info()[-1].tb_lineno
        error_desc = f"Exception occured in property_name_or_title_get : {line_no} -- {e}"
        print(error_desc)
    return property_name_or_title

def address_google_pin_address_get(page_html):
    address_google_pin_address = "-"
    try:
        ad_1 = page_html.xpath("//div[@class='title']//div[@class='info']//p[@class='city']//text()")[0].strip()
        ad_2 = page_html.xpath("//div[@class='title']//div[@class='info']//p[@class='location']//text()")[0].strip()
        address_google_pin_address = f'{ad_2} {ad_1}'
        address_google_pin_address =address_google_pin_address.replace("\r",'').replace("\t","").replace("\n",'')
    except Exception as e:
        line_no = sys.exc_info()[-1].tb_lineno
        error_desc = f"Exception occured in address_google_pin_address_get : {line_no} -- {e}"
        print(error_desc)
    return address_google_pin_address

def  date_available_get(page_html):
    date_available = "-"
    try:
        date_available = page_html.xpath("//div[@class='title']//div[@class='info']//p[@class='date']//text()")[0].strip()
    except Exception as e:
        line_no = sys.exc_info()[-1].tb_lineno
        error_desc = f"Exception occured in date_available_get : {line_no} -- {e}"
        print(error_desc)
    return date_available
        
def about_the_property_details_get(page_html):
    about_the_property_details = "-"
    try:
        about_the_property_details = ', '.join([ad.replace("\xa0","") for ad in page_html.xpath("//div[@class='description']//text()") if ad.strip()])
    except Exception as e:
        line_no = sys.exc_info()[-1].tb_lineno
        error_desc = f"Exception occured in about_the_property_details_get : {line_no} -- {e}"
        print(error_desc)
    return about_the_property_details

def rent_per_month_get(page_html):
    rent_per_month = "-"
    try:
        rent_per_month = ' '.join([pr.replace("month","").strip() for pr in page_html.xpath("//div[@class='title']//div[@class='price']//text()") if pr.strip()]).strip()
    except Exception as e:
        line_no = sys.exc_info()[-1].tb_lineno
        error_desc = f"Exception rent_per_month_get : {line_no} -- {e}"
        print(error_desc)
    return rent_per_month

def ameneties_get(page_html):
    Ameneties = []
    try:
        for items in page_html.xpath("//div[@class='details']//div[contains(@class,'detail')]"):
            key = items.text_content().strip()
            overview = html.tostring(items,encoding="unicode")
            val = "No" if "ion-close" in str(overview) else "Yes"
            overview_data= f'{key} {val}'
            Ameneties.append(overview_data)
        Ameneties = ", ".join(Ameneties)
    except:
        pass
    return Ameneties

def bedroom_get(page_html):
    bedroom = '-'
    try:
        for items in page_html.xpath("//div[@class='details']//div[contains(@class,'detail')]"):
            key = items.text_content().strip()
            overview = html.tostring(items,encoding="unicode")
            val = "No" if "ion-close" in str(overview) else "Yes"
            if "bedroom" in key.lower():
                bedroom = val
    except:
        pass
    return bedroom
    
def bathrooms_get(page_html):
    bathrooms = '-'
    try:
        for items in page_html.xpath("//div[@class='details']//div[contains(@class,'detail')]"):
            key = items.text_content().strip()
            overview = html.tostring(items,encoding="unicode")
            val = "No" if "ion-close" in str(overview) else "Yes"
            if "bathroom" in key.lower():
                bathrooms = val
    except:
        pass
    return bathrooms
    
def furnished_get(page_html):
    furnished = '-'
    try:
        for items in page_html.xpath("//div[@class='details']//div[contains(@class,'detail')]"):
            key = items.text_content().strip()
            overview = html.tostring(items,encoding="unicode")
            val = "No" if "ion-close" in str(overview) else "Yes"
            if "furnished" in key.lower():
                furnished = val
        return furnished
    except:
        pass
    
def phone_number_get(page_html):
    phone_number = "-"
    try:
        phn = page_html.xpath("//div[@class='contacts']//a/@href")
        phone_number = phn[0].replace("tel:","'")
    except:
        pass
    return phone_number

def images_link_get(page_html):
    images = '-'
    try:
        image_list = []
        img_list = page_html.xpath("//div[contains(@class,'single-product-slider')]//a")
        for img in img_list:
            imge = img.xpath(".//@href")
            if imge:
                imge_1 = "https://rentin.ae"+imge[0]
                image_list.append(imge_1)
        images = " , ".join(image_list)
    except:
        pass
    return images


data_list = []
for page in range(1,5):
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-US,en;q=0.9',
        'priority': 'u=0, i',
        'referer': 'https://rentin.ae/real-estate/rooms',
        'sec-ch-ua': '"Not A(Brand";v="8", "Chromium";v="132", "Google Chrome";v="132"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36',
    }

    params = {
        'page': page,
    }

    url = 'https://rentin.ae/real-estate/rooms'
    response = requests.get(url, params=params, headers=headers) # cookies=cookies,
    html_source = html.fromstring(response.content)
    page_source= requests.get(pdp_url,headers=headers)
    product_list = html_source.xpath("//div[contains (@class,'items-wrapper')]//div[contains (@class,'item-wrapper')]")
    for item in product_list:
        title_name = item.xpath(".//p[contains(@class,'heading')]//text()")[1]
        print(title_name)

        pdp_url = 'https://rentin.ae'+item.xpath(".//p[contains(@class,'heading')]/a/@href")[0]
        print(pdp_url)

        page_source= requests.get(pdp_url,headers=headers) 
        if page_source:
            page_html = html.fromstring(page_source.content)
            dict_data = {
                "Product link": "-",
                "Property type":"-",
                "Property Name or Title":"-",
                "Address / Google Pin address":"-",
                "About the property / Details":"-",
                "Bedrooms":"-",
                "Bathrooms":"-",
                "Room Furnishing":"-",
                "Rent per month":"-",
                "Security deposit":"-",
                "Bills":"-",
                "Preferred gender":"-",
                "Roomies preference":"-",
                "Date available":"-",
                "Phone Number":"-",
                "Ameneties for free":"-"
                }
            
            dict_data["Product link"] = pdp_url
            dict_data["Property type"] = property_type_get(page_html)
            dict_data["Property Name or Title"] = property_name_or_title_get(page_html)
            dict_data["Address / Google Pin address"]= address_google_pin_address_get(page_html)
            dict_data["Date available"] = date_available_get(page_html)
            dict_data["About the property / Details"] = about_the_property_details_get(page_html)
            dict_data["Rent per month"] = rent_per_month_get(page_html)
            dict_data["Ameneties for free"] = ameneties_get(page_html)
            dict_data["Bedrooms"] = bedroom_get(page_html)
            dict_data["Bathrooms"] = bathrooms_get(page_html)
            dict_data["Room Furnishing"] = furnished_get(page_html)
            dict_data["Phone Number"] = phone_number_get(page_html)
            dict_data["Images"] = images_link_get(page_html)

            data_list.append(dict_data)

df = pd.DataFrame(data_list)
df.to_csv("rentin_ae.csv",header=True,index=False)
