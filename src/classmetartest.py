# metar library: https://github.com/tomp/python-metar
from metar import Metar
import urllib2, string, time, datetime, csv
import pandas as pd
import numpy as np

class MetarHelper:

	metarDict = { }

	def get_weather_data_for_airports(self, airport_codes):
		ts = time.time()
		destFile = open("airports_metars_" + str(datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')), "w+")
		now = datetime.datetime.now()
		beginning = datetime.datetime.now() - datetime.timedelta(days=30)
		for code in airport_codes:
			if code is None:
				continue
			url = 'https://www.ogimet.com/display_metars2.php?lang=en&lugar=[[AIRPORT_CODE]]&tipo=ALL&ord=REV&nil=SI&fmt=txt&ano=[[YEAR_FROM]]&mes=[[MONTH_FROM]]&day=[[DAY_FROM]]&hora=01&anof=[[YEAR_TO]]&mesf=[[MONTH_TO]]&dayf=[[DAY_TO]]&horaf=23&minf=00&send=send'
			url = string.replace(url, '[[AIRPORT_CODE]]', str(code))
			url = string.replace(url, '[[YEAR_FROM]]', str(beginning.year))
			url = string.replace(url, '[[YEAR_TO]]', str(now.year))
			url = string.replace(url, '[[MONTH_FROM]]', str(beginning.month))
			url = string.replace(url, '[[MONTH_TO]]', str(now.month))
			url = string.replace(url, '[[DAY_FROM]]', str(beginning.day))
			url = string.replace(url, '[[DAY_TO]]', str(now.day))
			response = urllib2.urlopen(url)
			print ">>>>>>>>>>>> WEATHER INFO FOR {0} <<<<<<<<<<<<<<".format(code)
			# drop html prior to actual weather reports
			html = response.read().split("METAR/SPECI",1)[1]
			# remove 2 more lines
			html = html.split("\n",2)[2]
			# drop deep TAF reports section
			html = html.split("\n\n#",1)[0]
			self.get_distinct_metar_reports(html, destFile)
			response.close()  # best practice to close the file

	def get_distinct_metar_reports(self, body, destFile):
		linesTotal = len(body)
		print "total lines: ", linesTotal
		while(len(body.split("=",1)[1]) > 0):
			# '=' character is used as a separator between the reports
			report = body.split("=",1)[0]
			report = string.replace(report, "\n", " ")
			report = string.replace(report, "$", "")
			# remove extra whitespaces
			report = ' '.join(report.split())
			# create the dictionary key before dropping the datetime part of the report
			key = self.create_dict_key_from_metar(report)
			report = report[13:]
			# remove TEMPO elements, since the parser doesn't handle those well
			try:
				index = report.index("TEMPO")
				report = report[:index]
			except ValueError:
				1 == 1
			body = body.split("=",1)[1]
			# just to make sure the report string can be processed by our parser
			try:
				Metar.Metar(report)
				destFile.write(report + "\n")
				# create dictionary in form: ('AIRPORT_CODE', 'DATE_TIME'): 'METAR'
				if not key in self.metarDict:
					self.metarDict[key] = report
			except Metar.ParserError:
				print "could not parse report: ", report
			
	def create_dict_key_from_metar(self, report):
		date = report[:8]
		time = report[8:12]
		airportCode = report[19:23]
		key = (airportCode, date + "T" + time)		
		return key

	def find_most_accurate_metar(self, airport_code, year, month, day, time):
		key = (str(airport_code), str(year) + str(month).zfill(2) + str(day).zfill(2) + "T" + str(time).zfill(4))
		potentialEntries = {k: v for k, v in self.metarDict.items() if k[0] == airport_code and k[1].startswith(str(year) + str(month).zfill(2) + str(day).zfill(2))}
		smallestDiffMinutes = 9999
		smallestDiffKey = ()
		flightTime = datetime.datetime.strptime(str(year) + '-' + str(month).zfill(2) + '-' + str(day).zfill(2) + ' ' + str(time).zfill(4), '%Y-%m-%d %H%M')
		for metarKey, metar in potentialEntries.items():
			metarTime = datetime.datetime.strptime(metarKey[1], '%Y%m%dT%H%M')
			minutes_diff = abs((flightTime - metarTime).total_seconds() / 60.0)
			if(minutes_diff < smallestDiffMinutes):
				smallestDiffMinutes = minutes_diff
				smallestDiffKey = metarKey

		if smallestDiffKey in potentialEntries:
			#print "Found METAR for key {0}, time difference (minutes): {1}".format(key, smallestDiffMinutes)
			return potentialEntries[smallestDiffKey]
		else:
			print "no METAR found for requested key: %s" % (key,)
			#raise ValueError('no METAR found for requested key: ' + key)

	def get_weather_data(self, df):
		# parse the date & time
		# create URL to get METAR
		# parse the response
		print ""

	def write_metar_dict_to_csv(self):
		with open('metar_dictionary.csv', 'a') as f:  # Use 'wb' to erase previous work
			writer = csv.writer(f, delimiter=';')
			for key in self.metarDict:
				writer.writerow([key[0], key[1], self.metarDict[key]])

	def read_metar_dict_from_csv(self):
		with open('metar_dictionary.csv') as csvfile:
			reader = csv.reader(csvfile, delimiter=';')
			for row in reader:
				key = (row[0], row[1])
				report = row[2]
				if not key in self.metarDict:
					self.metarDict[key] = report
				#print "(" + row[0] + ", " + row[1] + "): " + row[2]

	def extract_sky_cover(self, cover_string):
			return {
				'CLR': 0,
				'SKC': 0,
				'FEW': 1,
				'SCT': 2,
				'BKN': 3,
				'OVC': 4,
				'VV': 4
			}.get(cover_string, None)
