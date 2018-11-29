#Remember,  since you're sending via the RESTful API (not MQTT)
#  1. we use IDs for commands 
#     (rather than AltIDs)
#  2. We use username/password 
#     (rather than the Landscape's Cert Bundle and the Device's Certificate/Private Key)
#
#
sSensorId     = 18
config_SetLED_command_capabilityID = '1c156fc1-be0e-4a5a-bf01-2326eef77e9e'
config_CommandName = "OnOff"  #(a Property of the Capability")
# Turn off the LED
config_CommandValue = "False"



import requests

from configparser import ConfigParser
parser = ConfigParser()
propFile = 'Greenhouse_02_Device.properties'
parser.read( propFile )

#find_sections = ['device', 'sensor', 'sensorType', 'capability']
#print( parser.get( propFile, 'deviceId' ) )

sBrokerUrl  = parser['Landscape']['url']
sUsername  = parser['Landscape']['Username']
sPassword  = parser['Landscape']['Password']

sDeviceId     = parser['device']['deviceId']



request_url='https://' + sBrokerUrl + '/iot/core/api/v1/devices/' + sDeviceId + '/commands'
headers={'Content-Type' : 'application/json'}
print('request_url: ' + request_url)
#>>>request_url: https://2f7241c1-8671-4591-9de0-8c64ed90e10e.canary.cp.iot.sap/iot/core/api/v1/devices/4/commands

payload='{ "capabilityId" : "' + config_SetLED_command_capabilityID + '", "sensorId" : "' + str( sSensorId ) + '", "command" : { "' + config_CommandName + '" : "' + config_CommandValue +'" } }'
print('payload: ' + payload)
#>>>payload: { "capabilityId" : "1c156fc1-be0e-4a5a-bf01-2326eef77e9e", "sensorId" : "7", "command" : { "OnOff" : "true" } }

response=requests.post(request_url, data=payload, headers=headers, auth=(sUsername, sPassword))

print(response.status_code)
#>>>200
print(response.text)
#>>>{"message":"Command issued successfully."}




