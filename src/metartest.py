# metar library: https://github.com/tomp/python-metar
from metar import Metar
import urllib2, string, time, datetime, csv

metarDict = { }

def extract_sky_cover(cover_string):
	return {
		'CLR': 0,
		'SKC': 0,
		'FEW': 1,
		'SCT': 2,
		'BKN': 3,
		'OVC': 4,
		'VV': 4
	}.get(cover_string, None)

def get_weather_data_for_airports(airport_codes):
	ts = time.time()
	destFile = open("airports_metars_" + str(datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')), "w+")
	now = datetime.datetime.now()
	beginning = datetime.datetime.now() - datetime.timedelta(days=30)
	for code in airport_codes:
		url = 'https://www.ogimet.com/display_metars2.php?lang=en&lugar=[[AIRPORT_CODE]]&tipo=ALL&ord=REV&nil=SI&fmt=txt&ano=[[YEAR_FROM]]&mes=[[MONTH_FROM]]&day=[[DAY_FROM]]&hora=01&anof=[[YEAR_TO]]&mesf=[[MONTH_TO]]&dayf=[[DAY_TO]]&horaf=23&minf=00&send=send'
		url = string.replace(url, '[[AIRPORT_CODE]]', code)
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
		get_distinct_metar_reports(html, destFile)
		response.close()  # best practice to close the file

def get_distinct_metar_reports(body, destFile):
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
		key = create_dict_key_from_metar(report)
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
			if not key in metarDict:
				metarDict[key] = report
		except Metar.ParserError:
			print "could not parse report: ", report
		
def create_dict_key_from_metar(report):
	date = report[:8]
	time = report[8:12]
	airportCode = report[19:23]
	key = (airportCode, date + "T" + time)		
	return key

def find_most_accurate_metar(airport_code, year, month, day, time):
	key = (airport_code, year + month + day + "T" + time)
	potentialEntries = {k: v for k, v in metarDict.items() if k[0] == airport_code and k[1].startswith('' + year + month + day)}
	print len(potentialEntries)
	# todo: function to find closest time of metars
	# 1. load the dictionary
	# 2. filter entries which satisfy airport & date condition
	# 3. find the METAR closest to a given arrival/departure time

# get a distinct list of all airports >>CHECKED<<
# get the METAR data for all these airports for whole month back => API calls from python >>CHECKED<<
# create dictionary in form [(AIRPORT_CODE, TIME), WEATHER STRING] >>CHECKED<<
# apply a function to all rows in the DataFrame that will:
# 	a) create access key based on airport code and time <<CHEKED>>
#	b) get the METAR string from the local dictionary
#	b) parse the string
#	c) set the necessary attributes in DF

def get_weather_data(df):
	print ""
	# parse the date & time
	# create URL to get METAR
	# parse the response

def write_metar_dict_to_csv():
	#fieldnames = [('airport_code', 'datetime')]
	with open('metar_dictionary.csv', 'wb') as f:  # Just use 'w' mode in 3.x
		writer = csv.writer(f, delimiter=';')
		for key in metarDict:
			writer.writerow([key[0], key[1], metarDict[key]])
		#w = csv.DictWriter(f, fieldnames, delimiter=';')
		#w.writeheader()
		#w.writerow(metarDict)	

def read_metar_dict_from_csv():
	with open('metar_dictionary.csv') as csvfile:
		reader = csv.reader(csvfile, delimiter=';')
		for row in reader:
			key = (row[0], row[1])
			report = row[2]
			if not key in metarDict:
				metarDict[key] = report
			print "(" + row[0] + ", " + row[1] + "): " + row[2]

metarString = """METAR KLAX 091153Z 11018KT 3SM +RA BR BKN005 BKN012 OVC025
                        15/15 A2967 RMK AO2 SLP044 VIS N
                        2 P0013 60015 7//// T01500150 10172
                        20150 56035="""

metarString = string.replace(metarString, "\n", " ")
metarString = string.replace(metarString, "$", "")
metarString = ' '.join(metarString.split())

print metarString

obs = Metar.Metar(metarString)

if obs.temp:
	print "temp: ", obs.temp.value()
if obs.wind_speed:
	print "wind_speed.value(): ", obs.wind_speed.value()
if obs.wind_speed_peak:
	print "wind_speed_peak.value(): ", obs.wind_speed_peak.value()
if obs.vis:
	print "vis: ", obs.vis.value()

index = 0
for skyi in obs.sky:
	(cover,height,cloud) = skyi
	print index
	print "cover: ", cover, " (", extract_sky_cover(cover), ")"
	print "height: ", height
	index+=1

print obs.string()

#######################################################################################

codes = ['EPWA', 'KLAX']

read_metar_dict_from_csv()
get_weather_data_for_airports(codes)
write_metar_dict_to_csv()
