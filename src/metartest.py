# metar library: https://github.com/tomp/python-metar
from metar import Metar
import urllib2, string, time, datetime

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
	for code in airport_codes:
		url = 'https://www.ogimet.com/display_metars2.php?lang=en&lugar=[[AIRPORT_CODE]]&tipo=ALL&ord=REV&nil=SI&fmt=txt&ano=2018&mes=01&day=01&hora=13&anof=2018&mesf=01&dayf=27&horaf=14&minf=00&send=send'
		url = string.replace(url, '[[AIRPORT_CODE]]', code)
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
		report = report[13:]
		# remove TEMPO elements, since the parser doesn't handle those well
		try:
			index = report.index("TEMPO")
			report = report[:index]
		except ValueError:
			1 == 1
		body = body.split("=",1)[1]
		# just to make sure the report string can be processed by our parser
		Metar.Metar(report)
		destFile.write(report + "\n")
		

# get a distinct list of all airports >>CHECKED<<
# get the METAR data for all these airports for whole month back => API calls from python >>CHECKED<<
# create dictionary in form [(AIRPORT_CODE, TIME), WEATHER STRING]
# apply a function to all rows in the DataFrame that will:
# 	a) create access key based on airport code and time
#	b) get the METAR string from the local dictionary
#	b) parse the string
#	c) set the necessary attributes in DF

def get_weather_data(airport_code, time):
	print ""
	# parse the date & time
	# create URL to get METAR
	# parse the response

#obs = Metar.Metar('METAR KEWR 111851Z VRB03G19KT 2SM R04R/3000VP6000FT TSRA BR FEW015 BKN040CB BKN065 OVC200 22/22 A2987 RMK AO2 PK WND 29028/1817 WSHFT 1812 TSB05RAB22 SLP114 FRQ LTGICCCCG TS OHD AND NW -N-E MOV NE P0013 T02270215')

#metarString = """METAR KLAX 191453Z 11005KT 7SM SCT009 OVC010 14/13 A3001
#                        RMK AO2 SLP163 SCT V BKN T01440133
#                        53001 $"""

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
get_weather_data_for_airports(codes)
