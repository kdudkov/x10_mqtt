# x10_mqtt
x10 mqtt daemon that acts as a gate between mqtt and x10/Ubiquiti mFi devices.
For x10 it uses [heyu binary](http://heyu.tanj.com/), for mfi - just api.

You can turn something on by sending 'ON' to /x10/{addr}/command, and listen status updates in /x10/{addr} if your X10 modules support getting status.

ideal for use with [openhab](http://www.openhab.org/)
