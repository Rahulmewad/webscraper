# -*- coding: utf-8 -*-
import re
import json
import scrapy
import random
import requests
import pandas as pd
from parsel import Selector
from numpy import random
from time import sleep
from urllib.parse import urljoin, quote

import TecAlliance.utility.cleaner as text_formatting
from TecAlliance.items import TecalliancePassengerCarsItem

# scrapy runspider audi_de_v3.py -a oem_id="9" -a product_code="VC"
class TecAllianceAudiDESpider(scrapy.Spider):
	name = 'audi_de_tecalliance_v4'

	def __init__(self, **kwargs):
		self.download_delay = 1
		# self.oem_id = kwargs.get("oem_id")  # oem_id
		# self.product_code = kwargs.get("product_code")  # oem_id
		# # row = jato_db.retrieve_oem_details(self.oem_id)
		# website Host
		self.home_domain = 'https://www.audi.de'
		self.head = {
			"Host": "www.audi.de",
			"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:104.0) Gecko/20100101 Firefox/104.0",
			"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
			"Accept-Language": "en-US,en;q=0.5",
			"Accept-Encoding": "gzip, deflate, br",
			"Connection": "keep-alive",
			"Upgrade-Insecure-Requests": "1",
			"Sec-Fetch-Dest": "document",
			"Sec-Fetch-Mode": "navigate",
		}
		self.company = "AUDI AG"
		self.manufacturer = "Audi"
		self.region = "DE"
		self.country_code = "de"
		
		self.data_to_export = []

	def start_requests(self):
		
		# using this API fetch all model url 
		# start_url="https://www.audi.de/de/brand/de/neuwagen.html?bycarlinegroup=a1"
		start_url="https://www.audi.de/de/brand/de/neuwagen.html"
		yield scrapy.Request(url=start_url, headers=self.head, callback=self.parse_models)

	def parse_models(self, response):
			models = response.xpath('//div[@data-testid="card"]')
			for model in models[0:]:
				print('---------------------------------------------------------')
				
				model_name = text_formatting.clean(model.xpath('.//p[@data-testid="carlineName"]/text()').extract_first())
				print("model_name::",model_name)
				
				model_url = urljoin(self.home_domain,
									model.xpath('.//a[@data-testid="discoverButton"]/@href').extract_first())
				print('~~~~~~~~~~~model url~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
				print(model_url)
				# target_model_id = model.xpath(".//@data-carlineid").extract_first()

				try:
					import requests
					from lxml import html

					headers = {
						"Host": "www.audi.de",
						"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:104.0) Gecko/20100101 Firefox/104.0",
						"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
						"Accept-Language": "en-US,en;q=0.5",
						"Accept-Encoding": "gzip, deflate, br",
						"Connection": "keep-alive",
						"Upgrade-Insecure-Requests": "1",
						"Sec-Fetch-Dest": "document",
						"Sec-Fetch-Mode": "navigate",
					}

					response = requests.get(model_url, headers=headers)
				
					# Parse the HTML content using lxml
					tree = html.fromstring(response.content)

					# Use XPath to find the "Technische Daten" link
					technische_daten_link = tree.xpath('//a[span[text()="Technische Daten"]]/@href')

					# Print the extracted technical data link
					engine_url = ''
					if technische_daten_link:
						engine_url = technische_daten_link[0].replace('#layer=/','https://www.audi.de/')
					else:
						print("Technische Daten link not found.")
						engine_url = ''
				except Exception as e:
					print(f"Failed to fetch engine_url for {model_name}: {str(e)}")
					engine_url = ''	
				print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
				print(engine_url)
				# engine_url = model_url.replace('.html', '/motor.html')
				# if model_name == 'e-tron GT quattro' or model_name == 'RS e-tron GT':
				# 	engine_url = model_url.replace('.html', '/antrieb.html')
				# 	print(engine_url)
					
				item = {
					"model_url": model_url,
					"engine_url": engine_url,
					"model_name": model_name,
				}
				if engine_url:
					yield scrapy.Request(url=engine_url, headers=self.head, callback=self.parse_url_parameters,
										meta={'previous_meta': item})
				else:
					print(f"Skipping {model_name} due to missing engine_url")	
						
	def parse_url_parameters(self, response):
		
		# response_html = requests.get(motor_url, headers=head)
		item = response.meta.get('previous_meta')	
		car_details = None

		try:
			car_details = json.loads(
				re.findall(r'SETUPS\.set\s*\(\s*\'nemo\.default\.data\s*\'\s*\,\s*(\{[^>]*?\}\})\)\;', response.text,
						   re.IGNORECASE)[0])
		except:
			pass

		# print("car_details::",car_details)
		model_year = car_details.get('configuration').get('modelyear')
		model_name = car_details.get('configuration').get('carlineNameBase')
		body_type = car_details.get('configuration').get('carlineNameSub')
		
		marketVersion = car_details.get('header').get('marketVersion')
		# manualRevision = json.loads(response.text).get('header').get('manualRevision')
		context = car_details.get('header').get('context')
		version = car_details.get('header').get('version')
		
		# SETUPS.set('nemo.url.modelsinfo', '/de/brand/de/neuwagen/a1/a1-sportback.modelsinfo.json');
		model_info_url = re.findall(r"SETUPS\.set\s*\(\'nemo\.url\.modelsinfo\'\,\s*\'([^>]*?)\'\s*\)", response.text,re.IGNORECASE)[0]
		car_info_url = re.findall(r"SETUPS\.set\s*\(\'nemo\.url\.carinfo\'\,\s*\'([^>]*?)\'\s*\)", response.text,re.IGNORECASE)[0]
		# print("model_info_url::",model_info_url)
		random_two_digit_number = random.randint(10, 99)
		random_six_digit_number = random.randint(100000, 999999)
		
		replace_string = f"info.{marketVersion}.{random_two_digit_number}.{random_six_digit_number}.json"
		# print("replace_string::",replace_string)
		# https://www.audi.de/de/brand/de/neuwagen/a1/a1-sportback.modelsinfo.mv-258.85.183333.json
		model_info_url = re.sub(r"info\.json", replace_string, model_info_url, flags=re.IGNORECASE)
		car_info_url = re.sub(r"info\.json", replace_string, car_info_url, flags=re.IGNORECASE)
		
		model_info_url = urljoin(self.home_domain, model_info_url)
		car_info_url = urljoin(self.home_domain, car_info_url)
		
		info_urls = {
			"model_info_url": model_info_url,
			"car_info_url": car_info_url,
			"model_year": model_year,
			"model_name": model_name,
			"body_type": body_type,
			"marketVersion": marketVersion,
		}
		
		items = {**item, **info_urls}

		yield scrapy.Request(url=model_info_url, headers=self.head, callback=self.parse_model_info,
							meta={'previous_meta': items})	
		
	def parse_model_info(self, response):
		with open("parse_model_info-DE.json", "w", encoding="utf-8") as f:
			f.write(response.text)
			
		item = response.meta.get('previous_meta')

		# car_info_response = requests.get(item.get('car_info_url'))	
		for block_id, tech_data in json.loads(response.text).get('models').items():
			print("##########################################################################")
			print(tech_data)
			
			# Extract and process the CO2 emission range
			co2_emission_range = tech_data.get("wltp-co2-combined")
			if co2_emission_range =='':
				co2_emission_range = tech_data.get("wltp-co2-weighted-combined")
			
			if co2_emission_range:
				co2_emission_to, co2_emission_from = co2_emission_range.split("–")
				co2_emission_to = co2_emission_to.replace('\xa0','').strip().replace(" g/km", "").replace("g/km", "")
				co2_emission_from = co2_emission_from.replace('\xa0','').strip().replace(" g/km", "").replace("g/km", "")
			else:
				co2_emission_from = None
				co2_emission_to = None

			spec_details = {
				'engine_description': tech_data.get("virtual-engine-description"), # "virtual-engine-description": "S line 40 TFSI S tronic",
				'virtual-engine-name': tech_data.get("virtual-engine-name"), # "virtual-engine-name": "40 TFSI",
				'steering_position_type': tech_data.get("steering"),
				'capacity': str(re.sub(r'\s*\(.*?\)', '', str(tech_data.get("virtual-power")))).replace('kW',''),
				'output_power_kw': tech_data.get("max-output-kw"),
				'output_power_hp': tech_data.get("max-output-ps"),
				'engine_reference': tech_data.get("engine-type"),
				'gearbox': tech_data.get("gearbox"),
				'drive_type': tech_data.get("transmission-type"),
				'brake_type': tech_data.get("brakes"),
				'energy_type': tech_data.get("fuel-type"),
				'co2_emission_standard': tech_data.get("emission-class"),
				'co2_emission_from': co2_emission_from,
				'co2_emission_to': co2_emission_to,
				'gross_vehicle_weight': tech_data.get("gross-weight-limit").replace('\\.', ',').replace('.',',').replace('Â', '').replace('\xa0', ' ').replace('Â kg','').replace('kg','').strip(),
				'model_id': block_id
			}
			spec_details = {key: ("" if value == "N/A" else value) for key, value in spec_details.items()}
			
			random_two_digit_number = random.randint(10, 99)
			random_six_digit_number = random.randint(100000, 999999)
			
			replace_string = f"info.{item.get('marketVersion')}.{random_two_digit_number}.{random_six_digit_number}.json"
			
			car_info_url = re.sub(r"info\.json", replace_string, item.get('car_info_url'), flags=re.IGNORECASE)
			print("block1111::",block_id, item.get("car_info_url"))
			item = {**item, **spec_details}
			itemm = {**item, **spec_details}
			results = []

			# Check if 'gross_vehicle_weight' key exists and contains "Sitzer"
			if 'gross_vehicle_weight' in itemm and 'Sitzer' in itemm['gross_vehicle_weight']:
				# Split the value of 'gross_vehicle_weight' by ";"
				cc = itemm['gross_vehicle_weight'].split(';')
				for tt in cc:
					# Extract seat count and corresponding gross vehicle weight
					seat_count = tt.split(':')[0].replace('Sitzer', '').strip()
					gross_vehicle_weight = tt.split(':')[1].replace('kg', '').strip()
					
					# Create a copy of the original itemm dictionary and add new keys
					new_item = itemm.copy()
					new_item['seat_count'] = seat_count
					new_item['gross_vehicle_weight'] = gross_vehicle_weight
					
					results.append(new_item)
			else:
				results.append(itemm)

			# Results data as a dictionary
			results_data = {'items': results}
			print(results_data)

			final_data = TecalliancePassengerCarsItem(
				vehicle_id = item.get('model_id'),
				company = self.company,
				region = self.region,
				brand = self.manufacturer,
				area_name = item.get('model_name'),
				composite_name = f"{item.get('model_name')} {item.get('body_type')} {item.get('engine_description')}",
				generation_year = item.get("model_year"),
				generation_sales_name = None,
				sales_geo_area = None,
				body_type = item.get('body_type'),
				body_type_sales_name = None,
				model_code = None,
				version_year = None,
				version_sales_name = None,
				vehicle_platform = None,
				market_segment = None,
				type_name = item.get('virtual-engine-name'),
				type_code_ = None,
				door_count = None,
				energy_type = None,
				steering_position_type = item.get('steering_position_type'),
				steering_box_type = None,
				power_transoutput_type = None,
				output_power_kw = item.get('output_power_kw'),
				output_power_hp = item.get('output_power_hp'),
				sales_horse_power_hp = None,
				capacity = item.get('capacity'),
				feature_configuration = None,
				start_of_production_from = None,
				end_of_production_to = None,
				start_of_sales_from = None,
				end_of_sales_to = None,
				emission_standard = item.get('co2_emission_standard'),
				seat_count = None,
				gross_vehicle_weight = item.get('gross_vehicle_weight'),
				co2_emission_from_kg = item.get('co2_emission_from'),
				co2_emission_to_kg = item.get('co2_emission_to'),
				power_train_type = None,
				drive_type = item.get('drive_type'),
				drive_type_sales_name = None,
				catalyst_type = None,
				voltage_type = None,
				gearbox = None,
				engine = None,
				brake_type = item.get('brake_type'),
				brake_disc_thickness = None,
				brake_outer_diameter = None,
				rim_measurement_type = None,
				suspension_type = None,
				wheel_suspension_type = None,
				wheel_count_type = None,
				brake_name = None,
				brake_system_type = None,
				engine_reference = item.get('engine_reference'),
				additional_code_engine = None,
				engine_sales_name = None,
				catalogue_display_code = None,
				aspiration_type = None,
				aspiration_intercooler = None,
				gearbox_reference = item.get('gearbox'),
				additional_code_gearbox = None,
				gearbox_sales_name = None,
				source_url_1 = item.get('engine_url'),
				source_url_2 = item.get('model_info_url'),
				source_url_3 = item.get('car_info_url'),
			)
			self.data_to_export.append(final_data)
		
	def closed(self, reason):
		if self.data_to_export:
			# Define your default header as a list of strings
			column_order = ["vehicle_id","company","region","brand","area_name","composite_name","generation_year","generation_sales_name","sales_geo_area","body_type","body_type_sales_name","model_code","version_year","version_sales_name","vehicle_platform","market_segment","type_name","type_code_","door_count","energy_type","steering_position_type","steering_box_type","power_transoutput_type","output_power_kw","output_power_hp","sales_horse_power_hp","capacity","feature_configuration","start_of_production_from","end_of_production_to","start_of_sales_from","end_of_sales_to","emission_standard","seat_count","gross_vehicle_weight","co2_emission_from_kg","co2_emission_to_kg","power_train_type","drive_type","drive_type_sales_name","catalyst_type","voltage_type","gearbox","engine","brake_type","brake_disc_thickness","brake_outer_diameter","rim_measurement_type","suspension_type","wheel_suspension_type","wheel_count_type","brake_name","brake_system_type","engine_reference","additional_code_engine","engine_sales_name","catalogue_display_code","aspiration_type","aspiration_intercooler","gearbox_reference","additional_code_gearbox","gearbox_sales_name","source_url_1","source_url_2","source_url_3"]  # Change this order as needed

			# Create a DataFrame with the specified column order
			df = pd.DataFrame(self.data_to_export, columns=column_order)

			# Save the DataFrame to a CSV file
			df.to_csv('MERIT_AUDI_DE_09082024.csv', index=False)
			self.log('Data saved to output.csv')




