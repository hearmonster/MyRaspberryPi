# create an IoTS device of choice with just one program
# and no necessary human interaction
# write a script for credential conversion

config_instance='2f7241c1-8671-4591-9de0-8c64ed90e10e.canary.cp.iot.sap'
config_user='root'
config_password='KaKLIDiu8QV527O'

config_crt_4_landscape='canary_cp_iot_sap_BUNDLE.crt'
# e.g. './eu10cpiotsap.crt'

config_NamesPrefix = 'Greenhouse'  # Used as a prefix for the Capability, Sensor Type, Sensor (instance) & Device (instance)
config_InstanceSuffix = '_02'     # Used as a suffix for the Sensor (instance) & Device (instance)

import sys
import requests
import json

capabilityName =  config_NamesPrefix + '_capability' #IoT AE is fussier than IoT Core. Take care to create Capability Names that IoT AE supports (Letters, Digits, Underscores & must start with a letter. No hyphens allowed!)
sensorTypeName =  config_NamesPrefix + '_sensorType'

# Sensor, Device and it's generated Cert file are *instances*, so include the suffix in their names...
sensorName =  config_NamesPrefix + config_InstanceSuffix + '_sensor'
deviceName = config_NamesPrefix + config_InstanceSuffix + '_device'

generatedCertFileName='./' + deviceName + '-cert.pem'
opensslFilenamesBase = deviceName + "-credentials"   #e.g. Greenhouse_01-device-credentials  (file extensions added later)
devicePropertiesFileName='./' + deviceName + '.properties'

# ======================================================================== 
# these values are filled as you go through the steps
gw_id_4_mqtt=''
my_deviceId = ''
my_deviceAltId = ''
my_capabilityId = ''
my_capabilityAltId = ''
my_sensorTypeId = ''
my_sensorTypeAltId = ''
my_sensorId = ''
my_sensorAltId = ''

# ======================================================================== 

print('listing gateways')
request_url='https://' + config_instance + '/iot/core/api/v1/gateways'
headers={'Content-Type' : 'application/json'}
response=requests.get(request_url, headers=headers, auth=(config_user, config_password))
status_code=response.status_code
if (status_code == 200):
	print(response.text)
	try:
		json_payload=json.loads(response.text)
		for individual_dataset in json_payload:
			print(individual_dataset['id'] + ' - ' + individual_dataset['protocolId'])
			if ((individual_dataset['protocolId'] == 'mqtt') and (individual_dataset['status'] == 'online')):
				gw_id_4_mqtt=individual_dataset['id']
				print('Using gateway: ' + gw_id_4_mqtt)
	except (ValueError) as e:
                print(e)
# ===

print('creating the device instance: ' + deviceName )
request_url='https://' + config_instance + '/iot/core/api/v1/devices'
headers={'Content-Type' : 'application/json'}
#payload='{ "gatewayId" : "' + gw_id_4_mqtt + '", "name" : "' + deviceName + '", "altId" : "' + deviceAltId + '" }'
payload='{ "gatewayId" : "' + gw_id_4_mqtt + '", "name" : "' + deviceName + '" }'
print(payload)
response=requests.post(request_url, headers=headers, auth=(config_user, config_password), data=payload)
status_code=response.status_code
print(str(status_code) + " " + str(response.text))
if (status_code == 200):
	try:
		json_payload = json.loads(response.text)
		my_deviceId = json_payload['id']
		print('Returned device ID: ' + my_deviceId )
		my_deviceAltId = json_payload['alternateId']
		print('Returned device AltID: ' + my_deviceAltId )
	except (ValueError) as e:
                print(e)
else:
	exit(0)
# ===

print('\nretrieving the certificate')
request_url='https://' + config_instance + '/iot/core/api/v1/devices/' + my_deviceId + '/authentications/clientCertificate/pem'
headers={'Content-Type' : 'application/json'}
response=requests.get(request_url, headers=headers, auth=(config_user, config_password))
status_code=response.status_code
print(str(status_code) + " " + str(response.text))
if (status_code == 200):
	try:
		json_payload = json.loads(response.text)
		secret = json_payload['secret']
		pem = json_payload['pem']
		print('Returned secret: ' + secret)
		print('pem: ' + pem)
		certfile=open( generatedCertFileName, "w")
		certfile.write(pem)
		certfile.close()

		pem_script=open("convert_" + deviceName + "-pem.sh", "w")

		pem_script.write("echo 'Please use pass phrase " + secret + " for the certificate import from " + generatedCertFileName + " in the conversion !'\n\n")

		pem_script.write("openssl rsa -in " + generatedCertFileName + " -out " + opensslFilenamesBase + ".key\n")
		pem_script.write("openssl x509 -in " + generatedCertFileName + " -out " +  opensslFilenamesBase + ".crt\n")
		pem_script.close()
	except (ValueError) as e:
                print(e)
else:
	exit(0)
# ===

print('\ncreating the capability:' + capabilityName)
request_url='https://' + config_instance + '/iot/core/api/v1/capabilities'
headers={'Content-Type' : 'application/json'}
propertyTemp     = '{ "name" : "' + config_NamesPrefix + '_temp", "dataType" : "float" }'
propertyHumidity = '{ "name" : "' + config_NamesPrefix + '_humidity", "dataType" : "float" }'
propertyLight    = '{ "name" : "' + config_NamesPrefix + '_light", "dataType" : "integer" }'
propertyLampSts  = '{ "name" : "' + config_NamesPrefix + '_lampStatus", "dataType" : "string" }'
capabilityProperties = propertyTemp + ', ' + propertyHumidity + ', ' + propertyLight + ', ' + propertyLampSts

#payload='{ "name" : "' + capabilityName + '", "properties" : [ ' + capabilityProperties + ' ], "altId" : "' + capabilityAltId + '" }'
payload='{ "name" : "' + capabilityName + '", "properties" : [ ' + capabilityProperties + ' ] }'
print(payload)
response=requests.post(request_url, headers=headers, auth=(config_user, config_password), data=payload)
status_code=response.status_code
print(str(status_code) + " " + str(response.text))
if (status_code == 200):
	try:
		json_payload = json.loads(response.text)
		my_capabilityId = json_payload['id']
		print('Returned capability ID: ' + my_capabilityId )
		my_capabilityAltId = json_payload['alternateId']
		print('Returned capability AltID: ' + my_capabilityAltId )
	except (ValueError) as e:
                print(e)
else:
	exit(0)
# ===


print('\ncreating the sensortype: ' + sensorTypeName )
request_url='https://' + config_instance + '/iot/core/api/v1/sensorTypes'
headers={'Content-Type' : 'application/json'}
payload='{ "name" : "' + sensorTypeName + '", "capabilities" : [ { "id" : "' + my_capabilityId + '", "type" : "measure" } ] }'
print(payload)
response=requests.post(request_url, headers=headers, auth=(config_user, config_password), data=payload)
status_code=response.status_code
print(str(status_code) + " " + str(response.text))
if (status_code == 200):
	try:
		json_payload=json.loads(response.text)
		my_sensorTypeId = json_payload['id']
		print('Returned sensorType ID: ' + my_sensorTypeId )
		my_sensorTypeAltId = json_payload['alternateId']
		print('Returned sensorType AltID: ' + my_sensorTypeAltId )
	except (ValueError) as e:
                print(e)
else:
	exit(0)
# ===

print('\ncreating the sensor instance: ' + sensorName )
request_url='https://' + config_instance + '/iot/core/api/v1/sensors'
headers={'Content-Type' : 'application/json'}
#payload='{ "name": "' + sensorName + '", "deviceId" : "' + my_deviceId + '", "sensorTypeId" : "' + my_sensorTypeId + '", "altId" : "' + sensorAltId + '" }'
payload='{ "name": "' + sensorName + '", "deviceId" : "' + my_deviceId + '", "sensorTypeId" : "' + my_sensorTypeId + '" }'
print(payload)
response=requests.post(request_url, headers=headers, auth=(config_user, config_password), data=payload)
status_code=response.status_code
print(str(status_code) + " " + str(response.text))
if (status_code == 200):
	try:
		json_payload = json.loads(response.text)
		my_sensorId = json_payload['id']
		print('Returned sensor ID: ' + my_sensorId )
		my_sensorAltId = json_payload['alternateId']
		print('Returned sensor AltID: ' + my_sensorAltId )
	except (ValueError) as e:
                print(e)
else:
	exit(0)
# ===


print("=== summary ===")
print("Device Name:\t" + deviceName + "\t ID: " + str(my_deviceId) + "\t\t\t altId: " + str(my_deviceAltId))
print("Sensor Name:\t" + sensorName + "\t ID: " + str(my_sensorId) + "\t\t\t altId: " + str(my_sensorAltId))
print("SensorType Name:\t" + sensorTypeName + "\t ID: " + str(my_sensorTypeId) + "\t altId: " + str(my_sensorTypeAltId))
print("Capability Name:\t" + capabilityName + "\t ID: " + str(my_capabilityId) + "\t altId: " + str(my_capabilityAltId))
#print("=== summary ===")

print("=== writing properties file: " + devicePropertiesFileName + "\t ===")
propfile=open( devicePropertiesFileName, "w")
propfile.write( "[device]\n")
propfile.write( "deviceName = " + deviceName + "\n" )
propfile.write( "deviceId = " + my_deviceId + "\n" )
propfile.write( "deviceAltId = " + my_deviceAltId + "\n" )
propfile.write( "\n")
propfile.write( "[sensor]\n")
propfile.write( "sensorName = " + sensorName + "\n" )
propfile.write( "sensorId = " + my_sensorId + "\n" )
propfile.write( "sensorAltId = " + my_sensorAltId + "\n" )
propfile.write( "\n")
propfile.write( "[sensorType]")
propfile.write( "sensorTypeName = " + sensorTypeName + "\n" )
propfile.write( "sensorTypeId = " + my_sensorTypeId + "\n" )
propfile.write( "sensorTypeAltId = " + my_sensorTypeAltId + "\n" )
propfile.write( "\n")
propfile.write( "[capability]")
propfile.write( "capabilityName = " + capabilityName + "\n" )
propfile.write( "capabilityId = " + my_capabilityId + "\n" )
propfile.write( "capabilityAltId = " + my_capabilityAltId + "\n" )
propfile.write( "\n")
propfile.write( "[properties] + "\n"")
#propfile.write( "payloadTemplate = '{ "capabilityAlternateId": "' + config_CapabilityAltId + '", "sensorAlternateId": "' + config_SensorAltId + '", "measures": [{"' + propertyTemp + '": "' + str( client.fSample_Temp ) + '","' + propertyHumidity + '": "' + str( client.fSample_Humidity ) + '","' + propertyLight + '": "' + str( client.iSample_Light ) + '", "' + propertyLampStatus + '": "' + str( client.sSample_LampStatus ) + '" }] }'
propfile.write( "\n")
propfile.close()
# ===
