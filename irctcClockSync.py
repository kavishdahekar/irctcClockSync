import urllib.request
import time
from datetime import datetime,timedelta
from dateutil import tz
import sys


# Settings
myTimeZone = "IST" #Your current timezone, Indian Standard Time

# We will fetch headers from an HTTP request to the irctc login page
queryPage = "https://www.irctc.co.in/eticketing/loginHome.jsf"


# needs admin priveleges
def _win_set_time(datetime):
	import os
	if os.system("date "+str(datetime.day)+"/"+str(datetime.month)+"/"+str(datetime.year)):
		print("Please run with administrator priveleges.")
		sys.exit(1)
	os.system("time "+str(datetime.hour)+":"+str(datetime.minute)+":"+str(datetime.second))
	print("Date set to : ",str(datetime.day)+"/"+str(datetime.month)+"/"+str(datetime.year))
	print("Time set to : ",str(datetime.hour)+":"+str(datetime.minute)+":"+str(datetime.second))

# needs admin priveleges
def _linux_set_time(datetime):
	import os

	retVal = os.system("sudo date --set '"+str(datetime.day)+"/"+str(datetime.month)+"/"+str(datetime.year)+" "+str(datetime.hour)+":"+str(datetime.minute)+":"+str(datetime.second)+"'")
	if retVal != 0:
		print("Please run with administrator priveleges.")
		sys.exit(1)
	print("Date set to : ",str(datetime.day)+"/"+str(datetime.month)+"/"+str(datetime.year))
	print("Time set to : ",str(datetime.hour)+":"+str(datetime.minute)+":"+str(datetime.second))


# --------------------------------------------------------------------------------------------
# irctc server time zone, as noticed from headers
from_zone = tz.gettz('GMT')
#User timezone : Indian Standard Time
to_zone = tz.gettz(myTimeZone)

start = time.time()
# actual http query
result = urllib.request.urlopen(queryPage)
end = time.time()

# round trip time of the query
rtt = end-start

# extract server date and time from the headers
headers = result.info()
server_datetime = datetime.strptime(headers['Date'],"%a, %d %b %Y %H:%M:%S GMT")

print("Server DateTime :",server_datetime)

# changing the timezone
server_datetime = server_datetime.replace(tzinfo=from_zone)
server_datetime = server_datetime.astimezone(to_zone)

# this time will be used for offsetting the time that was utilized for processing the recieved headers
tillNow = time.time()

# time that will be added as compensation
secondsToAdd = rtt/2 + (tillNow - end)

# calculating the final datetime
final_datetime = server_datetime + timedelta(seconds=secondsToAdd)
print("Adjusted DateTime :",str(final_datetime))

# apply the date and time according to the current platform
if sys.platform=='linux':
	print("\nPlatform : Linux\n")
	_linux_set_time(final_datetime)
elif  sys.platform=='win32':
	print("\nPlatform : Windows\n")
	_win_set_time(final_datetime)