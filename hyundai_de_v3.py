import scrapy
import json, random
from datetime import datetime, date
from playwright.sync_api import sync_playwright
from parsel import Selector
import time


# Main function
class HyundaiSpider(scrapy.Spider):
    name = 'hyundai_de_v3'
    allowed_domains = ['www.hyundai.com']
    # website Host 
    start_urls = ['https://www.hyundai.com/de/de/konfigurator/api/data/getAllModels.json']
    today_date_slug = date.today().strftime('%d%m%Y')

    # Csv data file formet current date name ex. MERIT_HYUNDAI_DE_07082024.csv
    custom_settings = {
        'FEEDS': {f'MERIT_HYUNDAI_DE_{today_date_slug}.csv': {'format': 'csv', 'overwrite': True}}
        }

    #Input: Self Object & Reponse from start_requests function
    #Output: Returns Response for List of model_url
    #Purpose: Will collect Make, Model & List of model urls, Api json_url and pass it to parse_item function
    def parse(self, response):
        data = json.loads(response.text)
        for row_num in range(len(data)):
            modelid = data[row_num].get('id')
            variant = data[row_num].get('trimlevels')
            for var_id in range(len(variant)):
                name = variant[var_id].get('name', '')
                model = variant[var_id].get('modelId', '')
                gen = variant[var_id].get('modelScp', '')
                body = variant[var_id].get('bodyId', '')
                trim = variant[var_id].get('trimId', '')
                json_url = 'https://www.hyundai.com/de/de/konfigurator/api/data/model/' + str(model) + '/gen/' + str(gen) + '/body/' + str(body) + '/trim/' + str(trim) + '/config.json?withAccessories&sections='
                model_url = 'https://www.hyundai.com/de/de/konfigurator/configure/{}/{}/{}/{}/trims/{}/summary'.format(name, model, gen, body, trim)

                data_points = {
                    'Model Code': modelid,
                    'json_url': json_url,
                    'model_url':model_url,
                }
                yield scrapy.Request(json_url, callback=self.parse_item, meta={'item_data': data_points})

    #Input: Self Object & Reponse from cparse function
    #Output: Generate CSV output
    #Purpose: Scrape required datapoints and Generate output
    def parse_item(self, response):
        item_data = response.meta['item_data']
        json_data = json.loads(response.text)
        # Function to safely get a value from a dictionary
        def safe_get(dictionary, key, default=''):
            return dictionary.get(key, default) if dictionary else default

        AreaName = json_data.get('name', '')
        # EnergyType =json_data.get('trimName', '')
        EnergyType_data =json_data.get('trimName', '')
        if 'select' in EnergyType_data.lower():
            EnergyType = ''
        else:
            EnergyType = EnergyType_data

        TypeName =json_data.get('className', '')

        # Check if 'carClasses' key is present, is a non-empty list, and has an element at index 0
        car_classes = json_data.get('carClasses')
        if car_classes and isinstance(car_classes, list) and car_classes[0]:
            BodyType = safe_get(car_classes[0], 'name', '')
        else:
            BodyType = ''
            
        hybrid_check_raw_data = json_data.get('configuration', {}).get('combFinal', {}).get('modelGroup', '')
        
        # Checking if hybrid_check_raw_data is not None and if the word "hybrid" is present in it
        if hybrid_check_raw_data is not None and 'hybrid' in hybrid_check_raw_data.lower():
            power_train_type = "Multi fuel"
        else:
            power_train_type = "Single fuel"
        output_power_kw = json_data.get('configuration', {}).get('combFinal', {}).get('power', '')
        output_power_hp = json_data.get('configuration', {}).get('combFinal', {}).get('powerPs', '')
        # co2_emission = json_data.get('configuration', {}).get('combFinal', {}).get('wltp', '')
        co2_emission = json_data.get('configuration', {}).get('combFinal', {}).get('emissionCombinedWltp', '')
        gross_vehicle_weight = json_data.get('configuration', {}).get('combFinal', {}).get('weightCoc', '')
        drive_type = json_data.get('configuration', {}).get('combFinal', {}).get('layout', '')
        rim_measurement_type = json_data.get('configuration', {}).get('rimRule', {}).get('info', '')
        generation_sales_name = json_data.get('configuration', {}).get('combFinal', {}).get('marketingName', '')
        
        #Co2 Emission and composite name fix, ticket TB-45
        print(f'+++++++++++ co2_emission raw: {co2_emission}')
        co2_emission_from = ''
        co2_emission_to = ''
        try:
            if co2_emission:
                if '-' in co2_emission:
                    co2_emission_from = co2_emission.split('-')[0]
                    co2_emission_to = co2_emission.split('-')[1]
                else:
                    co2_emission_from = co2_emission
                    co2_emission_to = co2_emission

        except Exception as e:
            print(f"++++++ exception error in co2_emission, url:{item_data['model_url']} error:{e}")


        try:
            # get composit name using playwright
            with sync_playwright() as pw:
                start_time = time.time()
                browser = pw.chromium.launch(headless=False)
                context = browser.new_context(viewport={"width": 1000, "height": 1080})
                page = context.new_page()
                # go to url
                page.goto(item_data['model_url'], timeout=0)
                wait_time_less = random.randint(5000,6000)
                page.wait_for_timeout(wait_time_less)

                if page.locator("h4[class='trim-motor-info-tablet ng-binding']").is_visible():
                    print(f'+++++++++++ composite name located')
                    wait_time_less = random.randint(1000,2000)
                    page.wait_for_timeout(wait_time_less)
                    content = Selector(text = page.content())
                    composite_slug = content.xpath('//h4[contains(@class,"trim-motor-info-tablet")]//text()').extract()
                    print(f"+++++++++ length of composite_slug: {len(composite_slug)} and it's type: {type(composite_slug)}, content:{composite_slug}")
                    composite_name = str(''.join(composite_slug)).replace('select','').replace('select','')
                else:
                    print(f"----------------- unable to locate composite name")
        except Exception as e:
            print(f"++++++++++seems like error while processing the url with playwright, url:{item_data['model_url']}, error: {e}")

        output_data = {
            'Region': 'DE',
            'Company': 'Hyundai',
            'Brand': 'Hyundai',
            'Area name': AreaName,
            'Composite Name': composite_name,
            'Generation Year': '',
            'Generation sales name': generation_sales_name,
            'Sales Geo Area type': 'Europe',
            'Body Type': TypeName,
            'Body Type sales name': '',
            'Model Code': item_data['Model Code'],
            'Version Year': '',
            'Version Sales name': '',
            'Vehicle Platform': '',
            'Market Segment': '',
            'Type Name': TypeName,
            'Type Code': '',
            'Door count': '',
            'Energy type': EnergyType,
            'Steering Position Type': 'Left Hand Side',
            'Output Type': '',
            'Output Power (kW) [1..n]': output_power_kw,
            'Output Power (HP) [1..n]': output_power_hp,
            'Sales Horse Power (HP)': output_power_hp,
            'Capacity': '',
            'Feature Configuration': '',
            'Sales Geo Area': 'Europe',
            'Start of Production (from)': '',
            'End of Production (to)': '',
            'Start of Sales (from)': '',
            'End of Sales (to)': '',
            'Emission Standard': '',
            'Gross Vehicle Weight': gross_vehicle_weight,
            'Co2 Emission from g/Km': co2_emission_from,
            'Co2 Emission to g/Km': co2_emission_to,
            'Power Train Type': power_train_type,
            'Drive Type': drive_type,
            'Drive Type Sales Name': '',
            'Catalyst Type': '',
            'Steering Box Type': '',
            'Voltage Type': '',
            'Gearbox type': '',
            'Engine [1..n] ': '',
            'Brake Type': '',
            'Brake Disc Thickness': '',
            'Brake Outer Diameter': '',
            'Rim Measurement Type Front': rim_measurement_type,
            'Rim Measurement Type Rear': rim_measurement_type,
            'Suspension Type': '',
            'Wheel suspension type': '',
            'Wheel Count Type': '',
            'Brake Name': '',
            'Brake System Type': '',
            'Engine': '',
            'Additional Code Engine': '',
            'Engine Sales Name': '',
            'Catalogue Display Code': '',
            'Aspiration Type': '',
            'Aspiration Intercooler': '',
            'Gearbox': '',
            'Additional Code Gearbox': '',
            'Gearbox Sales Name': '',
            'Url':item_data['model_url'],
            'Url_json':item_data['json_url'],
        }
        yield output_data

# Run the spider
if __name__ == "__main__":
    from scrapy.crawler import CrawlerProcess
    process = CrawlerProcess()
    process.crawl(HyundaiSpider)
    process.start()
