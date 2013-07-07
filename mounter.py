import subprocess

oldstate = "unknown"
text = subprocess.check_output(["mount"])
lines = filter(None, text.split('\n'))
for line in lines:
	if( line.find( "on / type" ) != -1 ):
		if( line.find( "barrier=0" ) != -1 ):
			oldstate = "fast"
		else:
			oldstate = "safe"
if oldstate == "unknown":
	print "unknown initial state, remounting safe"
	subprocess.call( ["mount", "/", "-o", "remount,barrier=1,commit=5"] )
	oldstate = "safe"

text = subprocess.check_output(["acpi","-b"])
lines = filter(None, text.split('\n'))

newstate = "unknown"
for line in lines:
	if line.startswith( "No support for device type: power_supply" ):
		newstate = "safe"
		break
	elif line.startswith( "Battery" ):
		if line.find("Charging") != -1:
			newstate = "fast"
			break
		elif line.find("Unknown") != -1:
			newstate = "safe"
			break
		elif line.find("Discharging") != -1:
			#if more than 10 minutes of battery, go fast
			timestr = line[ line.find("%, ") + 3 : line.find(" remaining") ]
			hr = timestr[0:2]
			min = timestr[3:5]
			sec = timestr[6:8]
			time = hr * 60 * 60 + min * 60 + sec
			if time > 600:
				newstate = "fast"
			else:
				newstate = "safe"
			break
if newstate == "unknown":
	print "unknown new state, newstate=safe, text:",text
	newstate = "safe"

if newstate != oldstate:
	if newstate == "safe":
		print "mounting safe"
		subprocess.call( ["mount", "/", "-o", "remount,barrier=1,commit=5"] )
	elif newstate == "fast":
		print "mounting fast"
		subprocess.call( ["mount", "/", "-o", "remount,barrier=0,commit=60"] )
	else:
		print "nothing to do"
