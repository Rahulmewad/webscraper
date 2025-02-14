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
# from scrapy.http import Request, FormRequest, JsonRequest
from urllib.parse import urljoin, quote, urlencode
from datetime import date


import TecAlliance.utility.cleaner as text_formatting
from TecAlliance.items import TecalliancePassengerCarsItem


class TecAllianceSkodaDESpider(scrapy.Spider):
	name = "skoda_de_tecalliance_v1"

	def __init__(self, **kwargs):
		self.download_delay = 1
		# self.oem_id = kwargs.get("oem_id")  # oem_id
		# self.product_code = kwargs.get("product_code")  # oem_id
		# # row = jato_db.retrieve_oem_details(self.oem_id)

		self.home_domain = "https://www.skoda-auto.de/"
		self.head = {
			"Host": "www.skoda-auto.de",
			"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:104.0) Gecko/20100101 Firefox/104.0",
			"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
			# "Accept-Language": "en-US,en;q=0.5",
			# "Accept-Encoding": "gzip, deflate, br",
			# "Connection": "keep-alive",
			# "Upgrade-Insecure-Requests": "1",
			# "Sec-Fetch-Dest": "document",
			# "Sec-Fetch-Mode": "navigate",
		}
		self.company = "Skoda Auto"
		self.manufacturer = "Skoda"
		self.region = "DE"
		self.country_code = "de"
		
		# self.snapshot_version = 'd1365a5d-56b0-41a3-9c7c-16c1eab91ab5'

		self.data_to_export = []
		
	def start_requests(self):
		# start_url = "https://cc.skoda-auto.com/c3pobe/version"
		start_url = "https://cc.skoda-auto.com/c3pobe/version?country=DEU"
		# payload = {"country": "DEU"}
		headers = {
				   "authority": "cc.skoda-auto.com",
				   "method": "POST",
				   "path": "/c3pobe/version",
				   "origin": "https://cc.skoda-auto.com",
				   "Referer": "https://cc.skoda-auto.com/deu/de-DE/",
				   "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
								 "Chrome/103.0.0.0 Safari/537.36",
				   "Accept": "application/json",
				   "Accept-Encoding": "gzip, deflate, br",
				   "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
				   "Content-Type": "application/json"
				}
		# yield scrapy.FormRequest(url=start_url, body=payload, callback=self.parse_homepage, headers=headers,
						  # dont_filter=True)
		yield scrapy.FormRequest(url=start_url, callback=self.parse_homepage, headers=headers,
				dont_filter=True)
	
	def parse_homepage(self, response):
		snapshot_version_str = response.text
		snapshot_version = snapshot_version_str.replace("\"", "")
		print(snapshot_version)
		items = {"snapshot_version": snapshot_version}
		start_url = "https://c3poweb.blob.core.windows.net/webcache/" + snapshot_version + "/homepage-DEU-de-DE.json"
		yield scrapy.Request(url=start_url, callback=self.parse_models, dont_filter=True, meta={'items': items})	
		

	# def start_requests(self):
		# start_url = f"https://c3poweb.blob.core.windows.net/webcache/{self.snapshot_version}/homepage-DEU-de-DE.json"
		# yield scrapy.Request(
			# url=start_url, callback=self.parse_models, dont_filter=True
		# )

	def parse_models(self, response):
		with open("SKODA - parse_model_info-PL.json", "w", encoding="utf-8") as f:
			f.write(response.text)
		
		item = response.meta["items"]
		snapshot_version = item.get('snapshot_version')
			
		jsonresponse = json.loads(response.text)
		valueslist = jsonresponse["groups"]
		allmodelslist = []
		for values_dict in valueslist:
			models_list = values_dict["tiles"]
			for models in models_list:
				basic_price = models["priceFrom"]
				model_name = models["title"].replace("&nbsp;", " ")
				print("______model", model_name)
				model_sub_name = models["subTitle"]
				model_id = models["modelId"]
				if model_id not in allmodelslist:
					allmodelslist.append(model_id)
					model_code = re.findall(r"skoda;[0-9]+;[a-zA-Z0-9]{2}", model_id)
					model_code_trimed = (
						"".join(model_code).replace("skoda;", "").split(";")
					)
					model_year = model_code_trimed[0]
					model_class = model_code_trimed[1]
					vehicle_key_junk = re.findall(
						r"skoda;[0-9]+;[a-zA-Z0-9]+;[0-9]{1};.*?;", model_id
					)
					vehicle_key_trimmed = (
						"".join(vehicle_key_junk).replace("skoda;", "").split(";")
					)
					unique_code1 = vehicle_key_trimmed[1]
					unique_code2 = vehicle_key_trimmed[3]
					vehicle_key = unique_code1 + "/" + unique_code2
					vehicle_key = vehicle_key.replace("\\", "/")
					car_code = re.findall(r"de-DE;;[0-9]+", model_id)[0].replace(
						"de-DE;;", ""
					)
					derivativepageurl = (
						f"https://c3poweb.blob.core.windows.net/webcache/{snapshot_version}/DEU/"
						+ model_year
						+ "/"
						+ model_class
						+ "/trimlines-de-DE.json"
					)
					# snapshot_version = "d1365a5d-56b0-41a3-9c7c-16c1eab91ab5"
					items = {
						"model_name": model_name,
						"model_year": model_year,
						"basic_price": basic_price,
						"model_class": model_class,
						"vehicle_key": vehicle_key,
						"snapshot_version": snapshot_version,
						"car_code": car_code,
						"derivativepageurl": derivativepageurl,
					}
					print("_________model", model_name)
					# if model_name in ('ENYAQ iV','ENYAQ COUPÉ iV','OCTAVIA','OCTAVIA COMBI',
					# 				  'FABIA','SCALA','KAMIQ','KAROQ','KODIAQ','SUPERB','SUPERB COMBI'):
					# if model_name in ('Kodiaq'):
					# if model_name in self.models_in_scope:

					data = {
						"Country": "DEU",
						"Culture": "de-DE",
						"ModelYear": model_year,
						"ModelClass": model_class,
						# "SnapshotVersion": snapshot_version
					}
					yield scrapy.Request(
						url=derivativepageurl,
						callback=self.derivative_list_page,
						dont_filter=True,
						meta={"items": items},
					)
					#
				# break
			# break

	def derivative_list_page(self, response):
		with open("SKODA - derivative_list_page-PL.json", "w", encoding="utf-8") as f:
			f.write(response.text)
		item = response.meta["items"]
		model_name = item["model_name"]
		model_year = item["model_year"]
		snapshot_version = item["snapshot_version"]
		model_class = item["model_class"]
		car_code = item["car_code"]
		jsonresponse = json.loads(response.text)
		trim_list = jsonresponse["items"]
		for trim_values in trim_list:
			trim_name = trim_values["name"].strip()
			# if trim_name in ('Style'):

			trim_id = trim_values["id"]
			default_color = trim_values["defaultColor"]
			model_id = trim_values["defaultModelId"]
			carlinename = trim_values["carlineName"]
			mbv_code = trim_values["mbvCode"]
			interior_code = trim_values["defaultInterior"]
			carline_code = trim_values["carline"]
			trimlineId = trim_id
			headers = {
				"authority": "cc.skoda-auto.com",
				"accept": "*/*",
				"accept-encoding": "gzip, deflate, br",
				"accept-language": "en-US,en;q=0.9",
				"referer": (
					"https://cc.skoda-auto.com/deu/de-DE/engine-scenic?activePage=engines&color="
					+ str(default_color)
					+ "&configurationId=&extraEquipments=GWC1WC1&id=DEU%3Bskoda%3B2023%3BPJ37M4%3B1%3BGYOQYOQ%3Bmda20230303062408%3Bde-DE%3B%3B60006%3B60006&interior="
					+ str(interior_code)
					+ "&modifiedPages=trimlines&snapshotVersion="
					+ str(snapshot_version)
					+ "&trimline="
					+ str(trim_id)
					+ "&visitedPages=trimlines%7Ccolors%7Cinteriors"
				),
				"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
			}

			engine_url = (
				"https://cc.skoda-auto.com/c3pobe/WebModel/Find?country=DEU&culture=de-DE&modelClass="
				+ str(model_class)
				+ "&modelYear="
				+ str(model_year)
				+ "&"
				+ "snapshotVersion="
				+ str(snapshot_version)
				+ "&trimlineId="
				+ str(trimlineId)
			)
			data = {
				"country": "DEU",
				"culture": "de-DE",
				"modelClass": str(model_class),
				"modelYear": str(model_year),
				"snapshotVersion": str(snapshot_version),
				"trimlineId": trim_id,
			}
			items = {
				**item,
				**{
					"model_name": model_name,
					"trim_name": trim_name,
					"model_id": model_id,
					"engine_url": engine_url,
					"model_id": model_id,
				},
			}
			url = "https://cc.skoda-auto.com/c3pobe/WebModel/Find?" + urlencode(data)
			print("_____url", url)
			if carline_code == car_code:
				yield scrapy.Request(
					url,
					callback=self.parse_engine,
					headers=headers,
					dont_filter=True,
					meta={"items": items},
				)
			# break

	def parse_engine(self, response):
		with open("SKODA - parse_engine-PL.json", "w", encoding="utf-8") as f:
			f.write(response.text)
		# print("____Res", response.text)
		items = response.meta["items"]
		trim_name = items["trim_name"]
		model_name = items["model_name"]
		model_year = items["model_year"]
		# snapshot_version = items["snapshot_version"]
		engine_url = items["engine_url"]
		print("items.get('derivativepageurl')::", items.get("derivativepageurl"))
		wheels_url = items.get("derivativepageurl").replace('trimlines-de-DE.json', 'wheels-de-DE.json')
		
		wheels_info = requests.get(wheels_url)
		
		wheels_data = json.loads(wheels_info.text)
		# print("_____________json",jsonresponse)

		print("trim_name::", trim_name)
		print("model_name::", model_name)
		print("model_year::", model_year)
		# print("snapshot_version::", snapshot_version)
		print("engine_url::", engine_url)

		for derivative_data in json.loads(response.text).get("models"):
			# derivative_data.get("")

			gross_vehicle_weight = None
			co2_emission_from = None
			co2_emission_to = None
			capacity = None
			type_name = None
			output_power_hp = None
			output_power_kw = None
			wheel_name = None
			engine_transmissio_electric = None
			
			default_wheel_code = derivative_data.get("defaultWheelCode")
			# print("default_wheel_code::",default_wheel_code)
			
			# for wheels in wheels_data.get("items").items():
			for wheels in wheels_data.get("items"):
				if wheels.get('id') == default_wheel_code:
					wheel_name = wheels.get("name")
					# print("Wheeelssss::", wheels.get("name"))
					break
				# input()
			
			for tech_data in derivative_data.get("technicalParameters").get("items"):
				# print("tech_data::", tech_data)

				if tech_data.get("id") == "KerbWeightMax":
					gross_vehicle_weight = (
						tech_data.get("value").replace(" ", "").replace("kg", "")
					)
				elif tech_data.get("id") == "ecs.primaryEmissionCombined":
					co2_emission_from = tech_data.get("minValue")
					co2_emission_to = tech_data.get("maxValue")
				elif tech_data.get("id") == "MaxPerformance":
					engine_transmissio_electric = tech_data.get("value").replace(",00", "")
					
			if engine_transmissio_electric is not None:
				engineName = f"{derivative_data.get('engineName')} {engine_transmissio_electric}"
			else:
				engineName = f"{derivative_data.get('engineName')}"
					
			# engineName = f"{derivative_data.get('engineName')} {engine_transmissio_electric}"
			composite_name = f"{items.get('model_name')} {items.get('trim_name')} {engineName}"
			
			try:
				if re.findall(r"(^\s*[\d.]+)\s*", engineName, flags=re.IGNORECASE):
					capacity = re.findall(
						r"(^\s*[\d.]+)\s*", engineName, flags=re.IGNORECASE
					)[0]
			except:
				pass
			output_power_kw = None
			try:
				output_power_kw = engine_transmissio_electric.replace(' kW', '')
			except:
				pass
				
			try:	
				if re.findall(r"^\s*[\d\,]+\s([A-Z]+)", engineName, flags=re.IGNORECASE):
					type_name = re.findall(
						r"^\s*[\d\,]+\s([A-Z]+)", engineName, flags=re.IGNORECASE
					)[0]
			except:
				pass
				
			try:
				if re.findall(r"([\d]+)\s*KM", engineName, flags=re.IGNORECASE):
					output_power_hp = re.findall(
						r"([\d]+)\s*KM", engineName, flags=re.IGNORECASE
					)[0]
			except:
				pass
				
			# try:
				# if re.findall(r"(\([\d]+\s*KM\)\s*[\d]+\s*kW)", engineName, flags=re.IGNORECASE):
					# capacity = re.findall(
						# r"(\([\d]+\s*KM\)\s*[\d]+\s*kW)", engineName, flags=re.IGNORECASE
					# )[0]
				# elif re.findall(r"([\d]+\s*kW)\s*(?:$|\s)", engineName, flags=re.IGNORECASE):
					# capacity = re.findall(
						# r"([\d]+\s*kW)\s*(?:$|\s)", engineName, flags=re.IGNORECASE
					# )[0]
				# elif re.findall(r"([\d]+\s*KM)\)?\s*(?:$|\s)", engineName, flags=re.IGNORECASE):
					# capacity = re.findall(
						# r"([\d]+\s*KM)\)?\s*(?:$|\s)", engineName, flags=re.IGNORECASE
					# )[0]	
			# except:
				# pass
			
			drive_type=None
			if re.findall("\s*4x4", derivative_data.get("transmissionName")):
				drive_type = "Allradantrieb"
			else:
				drive_type = "Frontanrieb"
				
			# try:
				# if re.findall(r"([\d]+)\s*kW", engineName, flags=re.IGNORECASE):
					# output_power_kw = re.findall(
						# r"([\d]+)\s*kW", engineName, flags=re.IGNORECASE
					# )[0]
			# except:
				# pass
				
				
			final_data = TecalliancePassengerCarsItem(
				vehicle_id=items.get("model_id"),
				company=self.company,
				region=self.region,
				brand=self.manufacturer,
				area_name=items.get("model_name"),
				composite_name=composite_name,
				generation_year=derivative_data.get("modelYear"),
				generation_sales_name=None,
				sales_geo_area=None,
				body_type=derivative_data.get("bodyworkName"),
				body_type_sales_name=None,
				model_code=None,
				version_year=derivative_data.get("modelYear"),
				version_sales_name=None,
				vehicle_platform=None,
				market_segment=None,
				type_name=type_name,
				type_code_=None,
				door_count=None,
				energy_type=derivative_data.get("fuelTypeName"),
				steering_position_type=None,
				steering_box_type=None,
				power_transoutput_type=None,
				output_power_kw=output_power_kw,
				output_power_hp=output_power_hp,
				sales_horse_power_hp=None,
				capacity=capacity,
				feature_configuration=None,
				start_of_production_from=None,
				end_of_production_to=None,
				start_of_sales_from=None,
				end_of_sales_to=None,
				emission_standard=None,
				gross_vehicle_weight=gross_vehicle_weight,
				co2_emission_from=co2_emission_from,
				co2_emission_to=co2_emission_to,
				power_train_type=None,
				drive_type=drive_type,
				drive_type_sales_name=None,
				catalyst_type=None,
				voltage_type=None,
				gearbox=None,
				engine=None,
				brake_type=None,
				brake_disc_thickness=None,
				brake_outer_diameter=None,
				rim_measurement_type=wheel_name,
				suspension_type=None,
				wheel_suspension_type=None,
				wheel_count_type=None,
				brake_name=None,
				brake_system_type=None,
				engine_reference=None,
				additional_code_engine=None,
				engine_sales_name=None,
				catalogue_display_code=None,
				aspiration_type=None,
				aspiration_intercooler=None,
				gearbox_reference=derivative_data.get("transmissionName"),
				additional_code_gearbox=None,
				gearbox_sales_name=None,
				source_url_1="https://cc.skoda-auto.com/deu/de-DE/",
				source_url_2=None,
				source_url_3=None,
			)

			extracted_data = {
				'Region': self.region,
				'Company': self.company,
				'Brand': self.manufacturer,
				'Area name': items.get("model_name"),
				'Composite Name': composite_name,
				'Generation Year': derivative_data.get("modelYear"),
				'Generation sales name': '',
				'Sales Geo Area type': 'Europe',
				'Body Type': derivative_data.get("bodyworkName"),
				'Body Type sales name': '',
				'Model Code': '',
				'Version Year': derivative_data.get("modelYear"),
				'Version Sales name': '',
				'Vehicle Platform': '',
				'Market Segment': '',
				'Type Name': type_name,
				'Type Code': '',
				'Door count': '',
				'Energy type': derivative_data.get("fuelTypeName"),
				'Steering Position Type': '',
				'Output Type': '',
				'Output Power (kW) [1..n]': output_power_kw,
				'Output Power (HP) [1..n]': output_power_hp, 
				'Sales Horse Power (HP)': '',
				'Capacity': capacity,
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
				'Power Train Type': '',
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
				'Rim Measurement Type Front': wheel_name,
				'Rim Measurement Type Rear': wheel_name,
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
				'Gearbox': derivative_data.get("transmissionName"),
				'Additional Code Gearbox': '',
				'Gearbox Sales Name': '',
				'Url': "https://cc.skoda-auto.com/deu/de-DE/",
				}

			self.data_to_export.append(extracted_data)

	def closed(self, reason):
		if self.data_to_export:

			column_order_new = ["Region","Company","Brand","Area name","Composite Name","Generation Year","Generation sales name","Sales Geo Area type","Body Type","Body Type sales name","Model Code","Version Year","Version Sales name","Vehicle Platform","Market Segment","Type Name","Type Code","Door count","Energy type","Steering Position Type","Output Type","Output Power (kW) [1..n]","Output Power (HP) [1..n]","Sales Horse Power (HP)","Capacity","Feature Configuration","Sales Geo Area","Start of Production (from)","End of Production (to)","Start of Sales (from)","End of Sales (to)","Emission Standard","Gross Vehicle Weight","Co2 Emission from g/Km","Co2 Emission to g/Km","Power Train Type","Drive Type","Drive Type Sales Name","Catalyst Type","Steering Box Type","Voltage Type","Gearbox type","Engine [1..n]","Brake Type","Brake Disc Thickness","Brake Outer Diameter","Rim Measurement Type Front","Rim Measurement Type Rear","Suspension Type","Wheel suspension type","Wheel Count Type","Brake Name","Brake System Type","Engine","Additional Code Engine","Engine Sales Name","Catalogue Display Code","Aspiration Type","Aspiration Intercooler","Gearbox","Additional Code Gearbox","Gearbox Sales Name","Url"]
			# Create a DataFrame with the specified column order

			df = pd.DataFrame(self.data_to_export, columns=column_order_new)

			# Save the DataFrame to a CSV file
			today_date_slug = date.today().strftime('%Y%m%d')
			df.to_csv(f"MERIT_SKODA_DE_{today_date_slug}.csv", index=False)
			self.log("Data saved to output.csv")
