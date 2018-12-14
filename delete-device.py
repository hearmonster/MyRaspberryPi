import requests

config_instance='2f7241c1-8671-4591-9de0-8c64ed90e10e.canary.cp.iot.sap'
config_user='root'
config_password='KaKLIDiu8QV527O'

config_my_device='24'
config_my_capability_down01='9c81b8e4-70d4-4859-ad03-aef334a03436'
config_my_capability_down02='88799ba3-0f78-40e3-91c5-0747c1cb2719'
config_my_sensor='32'

#--------------------------
# DELETE DEVICE (& SENSOR?)
request_url='https://' + config_instance + '/iot/core/api/v1/devices/' + config_my_device
headers={'Content-Type' : 'application/json'}

print('request_url: ' + request_url)

response=requests.delete(request_url, headers=headers, auth=(config_user, config_password))
print(response.status_code)
print(response.text)

