import requests
import json

config_instance='2f7241c1-8671-4591-9de0-8c64ed90e10e.canary.cp.iot.sap'
config_user='root'
config_password='KaKLIDiu8QV527O'

config_my_device='8'

request_url='https://' + config_instance + '/iot/core/api/v1/devices/' + config_my_device + '/measures?orderby=timestamp%20desc&skip=0&top=100'
headers={'Content-Type' : 'application/json'}
response=requests.get(request_url, headers=headers, auth=(config_user, config_password))
status_code=response.status_code
if (status_code == 200):
	print(response.text)
	try:
		json_payload=json.loads(response.text)
		for individual_measure in json_payload:
			print('value: ' + str(individual_measure['measure']))
	except (ValueError) as e:
                print(e)
