import requests

config_instance='2f7241c1-8671-4591-9de0-8c64ed90e10e.canary.cp.iot.sap'
config_user='root'
config_password='KaKLIDiu8QV527O'

config_my_device='8'
config_my_capability_down01='10fed9e7-4c34-4557-af1a-84c2d6c7ceff'
config_my_capability_down02='1bc34b1a-3aec-4719-8ee9-70345961b625'
config_my_sensor='5'
request_url='https://' + config_instance + '/iot/core/api/v1/devices/' + config_my_device + '/commands'

payload='{ "capabilityId" : "' + config_my_capability_down01 + '", "sensorId" : "' + config_my_sensor + '", "command" : { "p01_down01" : "value for p01_down01" , "p02_down01" : "value for p02_down01" } }'

headers={'Content-Type' : 'application/json'}

print('request_url: ' + request_url)
print('payload: ' + payload)

response=requests.post(request_url, data=payload, headers=headers, auth=(config_user, config_password))
print(response.status_code)
print(response.text)

payload='{ "capabilityId" : "' + config_my_capability_down02 + '", "sensorId" : "' + config_my_sensor + '", "command" : { "p01_down02" : "value for p01_down02" , "p02_down02" : "value for p02_down02" } }'

headers={'Content-Type' : 'application/json'}

print('request_url: ' + request_url)
print('payload: ' + payload)

response=requests.post(request_url, data=payload, headers=headers, auth=(config_user, config_password))
print(response.status_code)
print(response.text)
