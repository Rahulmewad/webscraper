import requests
from lxml import html
import re
import json
import pandas as pd


def headers_in_func():
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:132.0) Gecko/20100101 Firefox/132.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'Referer': 'https://www.sportsdirect.com/brands',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'Priority': 'u=0, i',
    }
    return headers


headers = headers_in_func()
response = requests.get('https://www.sportsdirect.com/adidas/view-all-adidas',headers=headers)


pdp_response_tree = html.fromstring(response.content)
pdp_data = pdp_response_tree.xpath("//ul[@id='navlist']//div[@class='s-productthumbbox']")
count = 0

data_dict_list = []
for pdp_data_in in pdp_data[0:1]:
    count+=1
    print('---------------',count)
    
    data_dict = {}

    pdp_product_link = 'https://www.sportsdirect.com'+pdp_data_in.xpath(".//div[@class='TextSizeWrap']//a[@href]/@href")[0].split('#')[0]
    print(pdp_product_link)
    

    pdp_product_name = ''.join(pdp_data_in.xpath(".//div[@class='TextSizeWrap']//span[@class='nameWrapTitle']//text()")).strip()
    print(pdp_product_name)
    
    pdp_product_price = ''.join(pdp_data_in.xpath(".//div[@class='s-largered']//text()")).replace('From','').strip()
    print(pdp_product_price)
    
    total_cout = pdp_response_tree.xpath("//div[@id='prdlistinformation']//span[@class='totalProducts']//text()")[0]
    response_data = requests.get(pdp_product_link, headers=headers)
    response_data_tree = html.fromstring(response_data.content)
    
    Website_Name = "sportsdirect"
    data_dict['Website_Name'] = Website_Name
    data_dict['Country'] = "UK"
    data_dict['Path_id'] = ""

    #1
    retailer_data_name = response_data_tree.xpath("//span[@class='prodTitle']//span[@id='lblProductName']//text()")[0]
    data_dict['retailer_data_name'] = retailer_data_name

    #2
    company_name = response_data_tree.xpath("//span[@class='brandTitle']//span[@id='lblProductBrand']//text()")[0]
    data_dict['company_name'] = company_name.strip()

    #3, #4
    ip_in_vat_prc_curr_local = response_data_tree.xpath("//div[@id='productDetails']//div[@class='originalprice']//span[@id='lblTicketPrice']//text()")[0].strip()
    min_cp_in_vat_prc_curr_local = response_data_tree.xpath("//div[@id='productDetails']//div[@class='pdpPrice']//span[@id='lblSellingPrice']//text()")[0].strip()
    if str(ip_in_vat_prc_curr_local)== str(min_cp_in_vat_prc_curr_local):
        data_dict['ip_in_vat_prc_curr_local']= ip_in_vat_prc_curr_local.strip()
        data_dict["min_cp_in_vat_prc_curr_local"] = ""
    else:
        data_dict['ip_in_vat_prc_curr_local']= ip_in_vat_prc_curr_local.strip()
        data_dict["min_cp_in_vat_prc_curr_local"] = min_cp_in_vat_prc_curr_local.strip()


    variant_data = json.loads(response_data_tree.xpath("//span[@class='ProductDetailsVariants hidden']/@data-variants")[0])[0]
    # for variant_col in variant_data[0:1]:

    images = [col['ImgUrlXXLarge'] for col in variant_data['ProdImages']['AlternateImages']]
    #5
    image = '; '.join(images)
    data_dict["image"] = image
    #6
    picture_cnt = len(images)
    data_dict["picture_cnt"] = picture_cnt
    #7
    color_group = variant_data['ColourName']
    data_dict["color_group"] = color_group

    size_variant = [size_var['SizeName'] for size_var in variant_data['SizeVariants'] if size_var['InStock'] == True]
    #10
    avail_size_list = '|'.join(size_variant)
    data_dict["avail_size_list"] = avail_size_list
    #11
    avail_size_cnt = len(size_variant)
    data_dict["avail_size_cnt"] = avail_size_cnt

    #12
    site_url = pdp_product_link
    data_dict['site_url'] = site_url

    #13
    retailer_id = response_data_tree.xpath("//div[@id='productInfo']//p[@class='productCode']//text()")
    retailer_id = ''.join(re.findall('\d+',str(retailer_id)))
    data_dict['retailer_id'] = retailer_id

    #14
    product_descr1 = response_data_tree.xpath("//div[@id='productInfo']//div[@class='productDescriptionInfoText']//text()")
    product_descr = ', '.join([des.strip() for des in product_descr1 if des.strip() != ''])
    data_dict['product_descr'] = product_descr

    #15
    len_product_descr = len(product_descr)
    data_dict['len_product_descr'] = len_product_descr

    
#     gender = response_data_tree.xpath("//div[@class='BreadcrumbGroupWrapper']//ol//a[@href]//text()")[1].strip()
#     data_dict['gender'] = gender
    

    #17
    category_path = response_data_tree.xpath("//div[@class='BreadcrumbGroupWrapper']//ol//a[@href]//text()")
    data_dict['category_path'] = '/'.join([path .strip() for path in category_path])

    #18
    shipping_Ex_Vat_Prc_Curr_Loc = response_data_tree.xpath("//ul[@id='deliveryDetails']//li[@id='delivery_Standard']//div//p[@class='price']//text()")[0].strip()
    data_dict['shipping_Ex_Vat_Prc_Curr_Loc'] = shipping_Ex_Vat_Prc_Curr_Loc

    #19.1,2
    size_variant = [size_var['SizeName'] for size_var in variant_data['SizeVariants'] if size_var['InStock'] == True]
    In_stock = ""
    out_of_stock = ""
    if size_variant:
        in_stock = "In Stock"
    else:
        out_of_stock = "Out of Stock"

    data_dict['in_stock'] = in_stock
    data_dict['out_of_stock'] = out_of_stock


    #19.3
    unavailable = ''
    try:
        price_one = response_data_tree.xpath("//div[@id='productDetails']//div[@class='originalprice']//span[@id='lblTicketPrice']//text()")[0].strip()
        price_two = response_data_tree.xpath("//div[@id='productDetails']//div[@class='pdpPrice']//span[@id='lblSellingPrice']//text()")[0].strip()
        if not price_one and not price_two:
            unavailable = "Unavailable"
    except:
        pass
    data_dict['unavailable'] = unavailable

    consumer_rating_avg = ''
    consumer_rating_cnt = ''
    gender = ''
    #8,9,16
    try:
        script_content = response_data_tree.xpath("//script[contains(text(), 'var dataLayerData')]/text()")[0]
        start_index = script_content.find("var dataLayerData = ") + len("var dataLayerData = ")
        end_index = script_content.find(";", start_index)
        data_layer_data = script_content[start_index:end_index]
        data_layer_dict = json.loads(data_layer_data)
        
        gender = data_layer_dict['productGender']
        
        product_id = data_layer_dict['productId']
        productSequenceNumber = data_layer_dict['productSequenceNumber']
        key_value = str(product_id)+'-'+str(productSequenceNumber)

        headers = {
            'sec-ch-ua-platform': '"Windows"',
            'Referer': 'https://www.sportsdirect.com/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
        }

        response_review = requests.get(
            'https://api.bazaarvoice.com/data/batch.json?passkey=caCoySjXiZzWpwg8yYLrGBS6PVsPrY5gAW7uS2GB6mnjU&apiversion=5.5&displaycode=19600-en_gb&resource.q0=products&filter.q0=id%3Aeq%3A368258-1918425&stats.q0=reviews&filteredstats.q0=reviews&filter_reviews.q0=contentlocale%3Aeq%3Aen*%2Cen_GB&filter_reviewcomments.q0=contentlocale%3Aeq%3Aen*%2Cen_GB&resource.q1=reviews&filter.q1=isratingsonly%3Aeq%3Afalse&filter.q1=productid%3Aeq%3A'+str(key_value)+'&filter.q1=contentlocale%3Aeq%3Aen*%2Cen_GB&sort.q1=submissiontime%3Adesc&stats.q1=reviews&filteredstats.q1=reviews&include.q1=authors%2Cproducts%2Ccomments&filter_reviews.q1=contentlocale%3Aeq%3Aen*%2Cen_GB&filter_reviewcomments.q1=contentlocale%3Aeq%3Aen*%2Cen_GB&filter_comments.q1=contentlocale%3Aeq%3Aen*%2Cen_GB&limit.q1=3&offset.q1=0&limit_comments.q1=3&callback=BV._internal.dataHandler0',
            headers=headers,
        )

        rev_json_data = re.search(r'BV\._internal\.dataHandler0\((.*)\)', str(response_review.text)).group(1)

        rev_json = json.loads(rev_json_data)
        rev_jj = rev_json['BatchedResults']['q1']['Includes']['Products'][key_value]['ReviewStatistics']

        consumer_rating_avg = rev_jj['AverageOverallRating']
        consumer_rating_cnt = rev_jj['TotalReviewCount']
         
    except:
        pass
    
    data_dict['gender'] = gender
    data_dict['consumer_rating_avg'] = consumer_rating_avg
    data_dict['consumer_rating_cnt'] = consumer_rating_cnt

    data_dict_list.append(data_dict)

df = pd.DataFrame(data_dict_list)
df.to_csv('PDP_URL_DATA_FILE.csv',header=True,index=False) 
