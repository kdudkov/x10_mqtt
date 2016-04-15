# x10_mqtt
x10 mqtt daemon that acts as a gate between mqtt and x10/Ubiquiti mFi devices.
For x10 it uses [heyu binary](http://heyu.tanj.com/), for mfi - just http api.

You can turn something on by sending 'ON' to `/x10/{addr}/command`, and listen status updates in `/x10/{addr}` if your X10 modules support getting status.

ideal for use with [openhab](http://www.openhab.org/)

## openhab config example:

items/mfi.items

```
Switch Mfi1 "Mfi_01 [%s]" <socket> (Living_Room) {mqtt="<[local:mpower/switch/plug01/1/relay:state:MAP(01.map)], >[local:mpower/switch/plug01/1/command:command:*:${command}]"}
Number Mfi1Power "Mfi_01 power [%.1f W]" <socket> (Living_Room,Power) {mqtt="<[local:mpower/switch/plug01/1/power:state:default]"}
```

transform/01.map

```
0=OFF
1=ON
```

