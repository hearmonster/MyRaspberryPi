#Remember, we use IDs (rather than AltIDs) for commands, 
# since you're sending via the RESTful API (not MQTT)
#
import requests
config_instance = '2f7241c1-8671-4591-9de0-8c64ed90e10e.canary.cp.iot.sap'
config_user = 'root'
config_password = 'KaKLIDiu8QV527O'
config_my_deviceID = '4'
config_my_sensorID = '9'
config_SetLED_command_capabilityID = '00a73ce7-3858-4c40-a4fd-9f47f355c485'  # "sampleDuration"
config_CommandName = "sampleDuration"  #(a Property of the Capability")
config_CommandValue = "60"  # unquoted values (e.g. 60) also can be sent - but would require canges below i.e. ... +str(sampleDuration)

request_url='https://' + config_instance + '/iot/core/api/v1/devices/' + config_my_deviceID + '/commands'
headers={'Content-Type' : 'application/json'}
print('request_url: ' + request_url)
#>>>request_url: https://2f7241c1-8671-4591-9de0-8c64ed90e10e.canary.cp.iot.sap/iot/core/api/v1/devices/4/commands

payload='{ "capabilityId" : "' + config_SetLED_command_capabilityID + '", "sensorId" : "' + config_my_sensorID + '", "command" : { "' + config_CommandName + '" : "' + config_CommandValue +'" } }'
print('payload: ' + payload)
#>>>payload: { "capabilityId" : "1c156fc1-be0e-4a5a-bf01-2326eef77e9e", "sensorId" : "7", "command" : { "OnOff" : "true" } }

response=requests.post(request_url, data=payload, headers=headers, auth=(config_user, config_password))

print(response.status_code)
#>>>200
print(response.text)
#>>>{"message":"Command issued successfully."}




