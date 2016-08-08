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
	os.system("date "+str(datetime.day)+"/"+str(datetime.month)+"/"+str(datetime.year))
	os.system("time "+str(datetime.hour)+":"+str(datetime.minute)+":"+str(datetime.second))
	print("Date set to : ",str(datetime.day)+"/"+str(datetime.month)+"/"+str(datetime.year))
	print("Time set to : ",str(datetime.hour)+":"+str(datetime.minute)+":"+str(datetime.second))


# haven't tested this yet, collaborators are free to test it
# http://stackoverflow.com/a/12292874/2175224
def _linux_set_time(time_tuple):
	import ctypes
	import ctypes.util
	import time

	# /usr/include/linux/time.h:
	#
	# define CLOCK_REALTIME					 0
	CLOCK_REALTIME = 0

	# /usr/include/time.h
	#
	# struct timespec
	#  {
	#	__time_t tv_sec;			/* Seconds.  */
	#	long int tv_nsec;		   /* Nanoseconds.  */
	#  };
	class timespec(ctypes.Structure):
		_fields_ = [("tv_sec", ctypes.c_long),
					("tv_nsec", ctypes.c_long)]

	librt = ctypes.CDLL(ctypes.util.find_library("rt"))

	ts = timespec()
	ts.tv_sec = int( time.mktime( datetime.datetime( *time_tuple[:6]).timetuple() ) )
	ts.tv_nsec = time_tuple[6] * 1000000 # Millisecond to nanosecond

	# http://linux.die.net/man/3/clock_settime
	librt.clock_settime(CLOCK_REALTIME, ctypes.byref(ts))


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
if sys.platform=='linux2':
	_linux_set_time(final_datetime)
elif  sys.platform=='win32':
	_win_set_time(final_datetime)