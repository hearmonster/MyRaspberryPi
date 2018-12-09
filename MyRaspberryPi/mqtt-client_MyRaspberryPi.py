#######################################################################################
#
# Refer to README.md for instructions and notes
#
 

import logging
config_logLevel = logging.INFO   #DEBUG, INFO, WARNING
#logging.basicConfig( filename = 'mqtt-client.log', level=logging.DEBUG )  #DEBUG, INFO, WARNING
logging.basicConfig( level=config_logLevel )  #DEBUG, INFO, WARNING

#from configparser import ConfigParser
#parser = ConfigParser()
#propFile = 'My_Raspberry_Pi[19]-Device.properties'
#parser.read( propFile )

#find_sections = ['device', 'sensor', 'sensorType', 'capability']
#print( parser.get( propFile, 'deviceId' ) )  

sBrokerUrl  = '2f7241c1-8671-4591-9de0-8c64ed90e10e.canary.cp.iot.sap'		#parser['Landscape']['url'] 
iBrokerPort = 8883								#int( parser['Landscape']['port'] )
sLandscapeCertBundleFilename   = './canary_cp_iot_sap_BUNDLE.crt'		#parser['Landscape']['CertBundle']
sDeviceCredentialsKeyFilename  = 'My_Raspberry_Pi[19]-Device-credentials.key'	#parser['device']['credentialsKey']
sDeviceCredentialsCertFilename = 'My_Raspberry_Pi[19]-Device-credentials.crt'	#parser['device']['credentialsCert']
sDeviceAltId = '84dedf1bdb564bd3'
sDevicePemSecret = '5iE6pZqCBhNAdmmD'



# DHT Sensor, Capability w/ 2x Properties
sSensorAltId_DHT 	= 'b1ebcfa471f8c87e'
sCapabilityAltId_DHT	= 'fb48689a05fdba88'
sPropertyName_DHTTemp	= 'temperature'
sPropertyName_DHTHum	= 'humidity'

# Light Sensor, Capability, Property
sSensorAltId_Light 	= 'abd3f4cc93b7fa50'
sCapabilityAltId_Light	= '625a5e85958ea7b5'
sPropertyName_LightInt	= 'LightIntensity'

# Lamp "Sensor" Property
sPropertyName_Lamp	= 'OnOff'

iSleepTime=3	#Sample Rate (in seconds).  e.g. 1800 => 30 mins between samples

logging.info( 'Broker URL:\t' + sBrokerUrl )
logging.info( 'Broker Port:\t ' + str( iBrokerPort ) )
logging.info( 'Device Alt ID:\t ' + sDeviceAltId )
#logging.info( 'Sensor Alt ID:\t ' + sSensorAltId )
#logging.info( 'Capability Alt ID: ' + sCapabilityAltId )
logging.info( 'Cert Bundle Filename: ' + sLandscapeCertBundleFilename )
logging.info( 'Cred Key Filename: ' + sDeviceCredentialsKeyFilename )
logging.info( 'Cred Cert Filename: ' + sDeviceCredentialsCertFilename )

# ========================================================================
# imports

import sys
import time
import ssl
from json import loads
from os import kill, getpid

# as an additional / non standard module pre-condition: 
# install Paho MQTT lib e.g. from https://github.com/eclipse/paho.mqtt.python
import paho.mqtt.client as mqtt

import grovepi

import sys
import os.path
filesToFind_set = [sLandscapeCertBundleFilename, sDeviceCredentialsKeyFilename, sDeviceCredentialsCertFilename]
for fileName in filesToFind_set:
	if not os.path.isfile( fileName ):
		print('Missing file: ', fileName )
		sys.exit()
logging.info( 'All files found, proceeding...')


# ========================================================================
# static configs

iDHtSensorPort = 7     #D7 (Digital, White)
iDHtSensorType = 3     #AM2302 https://www.dexterindustries.com/GrovePi/programming/python-library-documentation/
iLightSensorPort = 1   #A1 (Analog)
iLampPort = 5          #D5 (Digital)
iButtonPort = 4        #D4 (Digital)
iOverride = 0

grovepi.pinMode( iLampPort, "OUTPUT" )

# ========================================================================
def setLed( sOnOff_command_argument ):
	# Note: Takes a STRING (not a BOOL!) as an argument

	logging.debug( 'sOnOff_command_argument: ' + sOnOff_command_argument)
	#Advice is to never attempt a cast to Bool in python!  
	#	https://stackoverflow.com/questions/715417/converting-from-a-string-to-boolean-in-python

	client.bLEdState = isTrue( sOnOff_command_argument )

	#Toggle LED on Port D4
	#client.bLEdState = not client.bLEdState
	grovepi.digitalWrite( iLampPort, client.bLEdState )
	logging.info( 'LED Port: ' + str( iLampPort ) + '\tNew state: ' + str( client.bLEdState ) + '\n' )

	if client.bLEdState == True:
		client.sSample_LampStatus = 'ON'
	else:
		client.sSample_LampStatus = 'OFF'


def on_connect_brokerHandler(client, userdata, flags, rc):
	if rc==0:
		logging.info( 'connected OK [Returned code=' + str(rc) + ']' )
	else:
		logging.error( 'Bad connection [Returned code= ' + str(rc) + ']' )

def on_subscribeHandler(client, obj, message_id, granted_qos):
	logging.info('on_subscribe - message_id: ' + str(message_id) + ' / qos: ' + str(granted_qos) + '\n' )

def on_messageHandler(client, obj, msg):
	global iLampPort
	# print('on_message - ' + msg.topic + ' ' + str(msg.qos))
	logging.debug('Command Received (on_message):: Topic:' + msg.topic + '\t QoS:' + str(msg.qos) + '\t bPayload ' + msg.payload.decode('utf-8') )
	sPayload =  msg.payload.decode('utf-8')  #Required for Python 3.5 (str function fails)
	logging.debug( 'sPayload ' + sPayload )
	json_payload=loads( sPayload )  #(module: json.loads)
	if 'command' in json_payload:
		logging.debug(' Command discovered in payload' )
		command=json_payload['command']  #Just the subset of Command(s) and their Args
		#DO NOT ENABLE THIS!   logging.info( 'command(json_payload): ' + command ) << otherwise get 'dict implied conversion' error
		if 'OnOff' in json_payload['command']:
			logging.info('Command: "OnOff" discovered' )
			setLed( str(command['OnOff']) )
		if 'sampleDuration' in json_payload['command']:
			logging.info( 'Command: "sampleDuration" discovered' )
			logging.debug( 'New sample Duration discovered in payload: ' + str(command['sampleDuration']) + ' seconds' )
			#The following appears to work whether the number is wrapper in quotes or not!
			client.iSleepTime = command['sampleDuration']
			logging.info( 'New sample Duration now set to: ' + str( client.iSleepTime ) + ' seconds' )
			#Trigger a reset to the 'sampleRateHandler'
			kill( getpid(), signal.SIGUSR1 )  #(os.kill, os.getpid)
	else:
		logging.error( 'invalid command string - no "command" key found' )

def getDhtReadings():
	logging.debug( 'Obtaining Temperature and Humidity readings...' )
	[ fTemp, fHumidity ] = grovepi.dht( iDHtSensorPort, iDHtSensorType )
	logging.info( time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()) + '\tTemp reading: ' + str( fTemp ) + 'C\tHumidity reading: ' + str( fHumidity ) + '%' )
	client.fSample_Temp = fTemp + client.iOverride  #always safe to add it whether it's zero or non-zero
	client.fSample_Humidity = fHumidity
	if client.iOverride > 0:
		logging.info( 'Override invoked. Current Override value: ' + str( client.iOverride ) + '\tNew temp value: ' + str( client.fSample_Temp) )
	logging.debug( '"client" Object settings for Temp: ' + str( client.fSample_Temp ) + ' and Humidity: ' + str( client.fSample_Humidity ) )
               
def getLightReading():
	logging.debug( 'Obtaining Light reading...' )
	iLightSensorValue = grovepi.analogRead( iLightSensorPort )
	logging.info( time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()) + '\tlight reading: ' + str( iLightSensorValue ) + '\n' )
	client.iSample_Light = iLightSensorValue
	logging.debug( '"client" Object settings for Light: ' + str( client.iSample_Light ) )


def calculateOverride():
	isButtonPressed = grovepi.digitalRead( iButtonPort )
	if isButtonPressed:
		client.iOverride = client.iOverride + 1
		logging.info( 'Button depressed current state: TRUE   Override has increased to: ' + str( client.iOverride ) + '\n' )
	else:
		logging.debug( 'Button depressed current state: FALSE' )
		if  client.iOverride == 0:
			logging.debug( 'Override value cannot fall below zero')
		else:
			client.iOverride = client.iOverride - 1
			logging.info( 'Override value invoked but decreased to: ' + str( client.iOverride ) + '\n' )

def isTrue( s ):
	#Assumes 's' is any case:
	if s.upper() == "TRUE": 
		return True 
	elif s.upper() =="FALSE": 
		return False 
	else: 
		return exception
               
# === main starts here ===================================================

logging.info( 'Starting...' )

my_device=sDeviceAltId
client=mqtt.Client(client_id=my_device, clean_session=True, userdata=None)
client.on_connect=on_connect_brokerHandler
client.on_subscribe=on_subscribeHandler
client.on_message=on_messageHandler
client.tls_set(sLandscapeCertBundleFilename, certfile=sDeviceCredentialsCertFilename, keyfile=sDeviceCredentialsKeyFilename)
client.bConnectedFlag=False   #Custom property
client.bLEdState = True
client.iSleepTime = iSleepTime
client.continueLoop = True
client.iOverride = iOverride
client.fSample_Temp = 0
client.fSample_Humidity = 0
client.iSample_Light = 0
client.sSample_LampStatus = 'OFF'

# Set LED to its initial state
setLed( 'FALSE' )
#logging.info( 'LED Initial State:: Port: ' + str( iLampPort ) + '\tState: ' + str( client.bLEdState ) + '\n' )
#grovepi.digitalWrite( iLampPort, client.bLEdState )


#Enable logging for the MQTT Client
logger = logging.getLogger(__name__)
client.enable_logger(logger)

logging.info('Attempting connection to broker now...')
while not client.bConnectedFlag:
# {
	try:
		logging.debug('URL: ' + sBrokerUrl + '\tport: ' + str( iBrokerPort ) )
		client.connect(sBrokerUrl, port=iBrokerPort, keepalive=60)
		client.bConnectedFlag=True #set flag

	except (IOError,TypeError) as e:
		logging.info( 'Not connected yet. (client.bConnectedFlag = ' + str( client.bConnectedFlag ) + ')' )
		logging.debug( e )
		time.sleep(10)
# } end while

logging.info('Connected to broker.')

#Topic to publish measure readings to
my_publish_topic='measures/' + my_device

#Topic to listen for commands on
my_subscription_topic='commands/' + my_device
client.subscribe(my_subscription_topic, 0)

client.loop_start()
time.sleep( 5 )

from threading import Event
exit = Event()

def main():
	while client.continueLoop:
		exit.clear()
		logging.info('in main loop, sample duration set for ' + str( client.iSleepTime) + ' seconds\n' )
		while not exit.is_set():

			try:
				calculateOverride()

				getDhtReadings()
				sPayload='{ "capabilityAlternateId": "' + sCapabilityAltId_DHT + '", "sensorAlternateId": "' + sSensorAltId_DHT + '", "measures": {"' + sPropertyName_DHTTemp + '": "' + str( client.fSample_Temp ) + '","' + sPropertyName_DHTHum + '": "' + str( client.fSample_Humidity ) + '" } }'
				logging.debug('DHT Sensor Payload: ' + str(sPayload) + '\n')
				sResult=client.publish(my_publish_topic, sPayload, qos=0)
				logging.debug('result of publish for capability >>>DHT<<<  : ' + str(sResult) + '\n')
				if str(sResult[0]) != '0':
					logging.error('ERROR::return code of publish for capability >>>DHT<<<  : ' + str(sResult[0]) + '\tmid: ' + str(sResult[1]) + '\n')

				time.sleep(1)   # delay workaround for Bug:  https://forum.dexterindustries.com/t/dht-sensor-vs-light-sensor/904/2

				getLightReading()
				#sPayload='{ "capabilityAlternateId": "' + sCapabilityAltId_Light + '", "sensorAlternateId": "' + sSensorAltId_Light + '", "measures": {"' + sPropertyName_LightInt + '": "' + str( client.iSample_Light ) + '", "' + propertyLampStatus + '": "' + str( client.sSample_LampStatus ) + '" } }'
				sPayload='{ "capabilityAlternateId": "' + sCapabilityAltId_Light + '", "sensorAlternateId": "' + sSensorAltId_Light + '", "measures": {"' + sPropertyName_LightInt + '": "' + str( client.iSample_Light ) + '" } }'
				logging.debug('Light Sensor Payload: ' + str(sPayload) + '\n')
				sResult=client.publish(my_publish_topic, sPayload, qos=0)
				logging.debug('result of publish for capability >>>Light<<<  : ' + str(sResult) + '\n')
				if str(sResult[0]) != '0':
					logging.error('ERROR::return code of publish for capability >>>Light<<<  : ' + str(sResult[0]) + '\tmid: ' + str(sResult[1]) + '\n')

			except (IOError,TypeError) as e:
				logging.error( 'Error' )

			#time.sleep( client.iSleepTime )
			exit.wait( client.iSleepTime )
	#Clean up...
	logging.info( 'All done!' )
	client.loop_stop()    #Stop loop 
	client.disconnect() # disconnect
	setLed( 'FALSE' )

# These two listeners will handle the Sample Duration reset and the "real" events (such as keyboard ^C)
def on_sampleRateHandler(signo, _frame):
	# Ironically enough, this doesn't appear to *do* anything! But it actually *does*, but only subtly...
	# The 'exit.set()' below will trigger an immediate exit from the loop
	# The loop will see the 'client.continueLoop' property continues to be True and will rerun the loop...but with a new sleep time!
	# Ultimately, I get a premature exit from this sleep cycle and the loop restarts *immediately*...but with a new sleep time!
	logging.warning('SIGUSR1 gentle reset...\n' )
	# client.continueLoop continues to be true
	exit.set()

def on_quitHandler(signo, _frame):
	# sets the 'client.continueLoop' property to False, then returns control back to the main() loop
	# The 'exit.set()' below will trigger an immediate exit from the loop
	# The loop will see the 'client.continueLoop' property has been set to False and will "refuse" to rerun the loop
	# resulting in the clean up commands being run just before main() terminates
	logging.warning('Interrupted by %d' % signo)
	logging.warning('shutting down...' )
	client.continueLoop = False
	exit.set()



if __name__ == '__main__':

	import signal

	#Register a Signal Handler for my sample reset function
	signal.signal(signal.SIGUSR1, on_sampleRateHandler )

	#Register 3 Signal Handlers (all to the same event handler function)
	for sig in ('TERM', 'HUP', 'INT' ):
		signal.signal(getattr(signal, 'SIG'+sig), on_quitHandler);

	logging.debug( 'Starting Main...!' )
	main()
