#Remember,  since you're sending via the RESTful API (not MQTT)
#  1. we use IDs for commands 
#     (rather than AltIDs)
#  2. We use username/password 
#     (rather than the Landscape's Cert Bundle and the Device's Certificate/Private Key)
#
#
config_SetSampleDuration_command_capabilityID = '00a73ce7-3858-4c40-a4fd-9f47f355c485'
config_CommandName = "sampleDuration"  #(a Property of the Capability")

# grab the new duration as an argument, default to 30 secs if not a valid number
import sys                
sCommandArg = sys.argv[1]
import numbers

#check if Arg[1] a parsable int
try:
	x = int( sCommandArg )
	sCommandValue = sCommandArg
except ( ValueError ) as e:
	print( sCommandArg + ' is not a valid number, defaulting to 30 secs' )
	sCommandValue = str( 30 )


# Iteration over all arguments:
for eachArg in sys.argv:   
        print(eachArg)

import requests

from configparser import ConfigParser
parser = ConfigParser()



tenantPropFile = '/home/pi/MyRaspberryPi/tenant.properties'
parser.read( tenantPropFile )

devicePropFile = 'My-Raspberry-Pi_Device.properties'
parser.read( devicePropFile )

#find_sections = ['device', 'sensor', 'sensorType', 'capability']
#print( parser.get( propFile, 'deviceId' ) )

sBrokerUrl  = parser['Landscape']['url']
sUsername  = parser['Landscape']['Username']
sPassword  = parser['Landscape']['Password']
sSensorId = parser['sensors']['sensorId_SampleDuration']  #String, not int
sDeviceId = parser['device']['deviceId']  #String, not int




request_url='https://' + sBrokerUrl + '/iot/core/api/v1/devices/' + sDeviceId + '/commands'
headers={'Content-Type' : 'application/json'}
print('request_url: ' + request_url)
#>>>request_url: https://2f7241c1-8671-4591-9de0-8c64ed90e10e.canary.cp.iot.sap/iot/core/api/v1/devices/4/commands

payload='{ "capabilityId" : "' + config_SetSampleDuration_command_capabilityID + '", "sensorId" : "' + sSensorId + '", "command" : { "' + config_CommandName + '" : "' + sCommandValue +'" } }'
print('payload: ' + payload)
#>>>payload: { "capabilityId" : "1c156fc1-be0e-4a5a-bf01-2326eef77e9e", "sensorId" : "7", "command" : { "OnOff" : "true" } }

response=requests.post(request_url, data=payload, headers=headers, auth=(sUsername, sPassword))

print(response.status_code)
#>>>200
print(response.text)
#>>>{"message":"Command issued successfully."}




