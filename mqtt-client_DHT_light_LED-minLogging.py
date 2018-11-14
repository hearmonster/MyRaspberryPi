#######################################################################################
#
# Connects to my Canary instance 
#
# Configurable logging implemented (writes to std out, but file output is commented out)
#
# Captures DHT and Light (with a five second delay between the two to prevent locking the bus)
#
# Accepts Commands - parses out the command and payload
#	to toggle the LED - command: "OnOff", 
#		* accepts TRUE/FALSE (case insenstive)
#	to reset the sample duration - command "sampleDuration"
#		* accepts INT (seconds) either wrapped in quotes or not
#		* interupts the current wait immediately, 
#		  (implemented using Python Events and OS Signal Interupts)
#
# Shuts down gracefully (disconnects from MQTT Broker)
#
#

config_broker_url='2f7241c1-8671-4591-9de0-8c64ed90e10e.canary.cp.iot.sap'
config_broker_port=8883
config_alternate_id_device='694b3a57781cad0e'      #declares Broker TOPIC.  ie 'GrovePi'
config_alternate_id_capability_up01='fb48689a05fdba88'   #ie 'GetTemperatureAndHumidity'
config_alternate_id_sensor='cbfdb4c7055403cb'  #ie 'DHT sensor'
config_crt_4_landscape='./canary_cp_iot_sap_BUNDLE.crt'
config_sleep_time=20	#1800    #30 mins between samples
config_credentials_key='./credentials.key'
config_credentials_crt='./credentials.crt'

# ========================================================================
# imports

import sys
import time
import logging
import ssl
from json import loads
from os import kill, getpid

# as an additional / non standard module pre-condition: 
# install Paho MQTT lib e.g. from https://github.com/eclipse/paho.mqtt.python
import paho.mqtt.client as mqtt

import grovepi



# ========================================================================
# static configs

iDHtSensorPort = 7     #D7 (Digital)
iLightSensorPort = 1   #A1 (Analog)
#logging.basicConfig( filename = 'mqtt-client.log', level=logging.DEBUG )  #DEBUG, INFO, WARNING
logging.basicConfig( level=logging.INFO )  #DEBUG, INFO, WARNING
iLEdPort = 4            #D4 (Digital)

# ========================================================================
def setLed( sOnOff_command_argument ):
	logging.info( 'sOnOff_command_argument: ' + sOnOff_command_argument)
	#Advice is to never attempt a cast to Bool in python!  
	#	https://stackoverflow.com/questions/715417/converting-from-a-string-to-boolean-in-python

	client.bLEdState = isTrue( sOnOff_command_argument )

	#Toggle LED on Port D4
	#client.bLEdState = not client.bLEdState
	grovepi.digitalWrite( iLEdPort, client.bLEdState )
	logging.info( "Port: " + str( iLEdPort ) + "\tState: " + str( client.bLEdState ) + "\n" )


def on_connect_brokerHandler(client, userdata, flags, rc):
	if rc==0:
		logging.info( "connected OK [Returned code=" + str(rc) + "]" )
	else:
		logging.error( "Bad connection [Returned code= " + str(rc) + "]" )

def on_subscribeHandler(client, obj, message_id, granted_qos):
	logging.info('on_subscribe - message_id: ' + str(message_id) + ' / qos: ' + str(granted_qos) + '\n' )

def on_messageHandler(client, obj, msg):
	global iLEdPort
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
			logging.info( 'New sample Duration: ' + str(command['sampleDuration']) + ' seconds' )
			#The following appears to work whether the number is wrapper in quotes or not!
			client.iSleepTime = command['sampleDuration']
			#Trigger a reset to the 'sampleRateHandler'
			kill( getpid(), signal.SIGUSR1 )  #(os.kill, os.getpid)
	else:
		logging.error( "invalid command string - no 'command' key found" )

def getDhtReadings():
	logging.info( "Obtaining Temperature and Humidity readings..." )
	[ iTemp, iHumidity ] = grovepi.dht( iDHtSensorPort, 0 )
	logging.info( "Temp: " + str( iTemp ) + "C\tHumidity: " + str( iHumidity ) + "%" )
	sPayload='{ "capabilityAlternateId": "fb48689a05fdba88", "sensorAlternateId": "cbfdb4c7055403cb", "measures": [{"temperature": "' + str(iTemp) + '" },{"humidity": "' + str(iHumidity) + '" }] }'
	logging.debug( "published for capability >>>GetTemperatureAndHumidity<<<  payload: " + sPayload )
	return sPayload
               
def getLightReading():
	logging.info( "Obtaining Light reading..." )
	iLightSensorValue = grovepi.analogRead( iLightSensorPort )
	logging.info( "light reading: " + str( iLightSensorValue ) )
	sPayload='{ "capabilityAlternateId": "e9df11f2c54275f4", "sensorAlternateId": "e1a42e1a61e3a5ae", "measures": [{"sample": "' + str( iLightSensorValue ) + '" }] }'
	sResult=client.publish(my_publish_topic, sPayload, qos=0)
	logging.debug( "published for capability >>>GetLight<<<  payload: " + sPayload )
	return sPayload

def isTrue( s ):
	#Assumes 's' is any case:
	if s.upper() == "TRUE": 
		return True 
	elif s.upper() =="FALSE": 
		return False 
	else: 
		return exception
               
# === main starts here ===================================================

logging.info( "Starting..." )

my_device=config_alternate_id_device
client=mqtt.Client(client_id=my_device, clean_session=True, userdata=None)
client.on_connect=on_connect_brokerHandler
client.on_subscribe=on_subscribeHandler
client.on_message=on_messageHandler
client.tls_set(config_crt_4_landscape, certfile=config_credentials_crt, keyfile=config_credentials_key)
client.bConnectedFlag=False   #Custom property
client.bLEdState = True
client.iSleepTime = config_sleep_time
client.continueLoop = True

# Set LED to its initial state
logging.info( "LED Initial State:: Port: " + str( iLEdPort ) + "\tState: " + str( client.bLEdState ) + "\n" )
grovepi.digitalWrite( iLEdPort, client.bLEdState )


#Enable logging for the MQTT Client
logger = logging.getLogger(__name__)
client.enable_logger(logger)

logging.info("Attempting connection to broker now...")
while not client.bConnectedFlag:
# {
	try:
		client.connect(config_broker_url, port=config_broker_port, keepalive=60)
		client.bConnectedFlag=True #set flag

	except (IOError,TypeError) as e:
		logging.info( "Not connected yet. (client.bConnectedFlag = " + str( client.bConnectedFlag ) + ")" )
		time.sleep(10)
# } end while

logging.info("Connected to broker.")

my_publish_topic='measures/' + my_device
my_subscription_topic='commands/' + my_device
client.subscribe(my_subscription_topic, 0)

client.loop_start()
time.sleep( 10 )

from threading import Event
exit = Event()

def main():
	while client.continueLoop:
		exit.clear()
		while not exit.is_set():
			logging.info('in main loop, sample duration set for ' + str( client.iSleepTime) + ' seconds\n' )

			try:
				sPayload = getDhtReadings()
				sResult=client.publish(my_publish_topic, sPayload, qos=0)
				logging.info("result of publish for capability >>>GetTemperatureAndHumidity<<<  : " + str(sResult) + "\n")

				time.sleep(5)   # delay workaround for Bug:  https://forum.dexterindustries.com/t/dht-sensor-vs-light-sensor/904/2

				sPayload = getLightReading()
				sResult=client.publish(my_publish_topic, sPayload, qos=0)
				logging.info("result of publish for capability >>>GetLight<<<  : " + str(sResult) + "\n")

			except (IOError,TypeError) as e:
				logging.error( "Error" )

			#time.sleep( client.iSleepTime )
			exit.wait( client.iSleepTime )
	logging.info( 'All done!' )
	client.loop_stop()    #Stop loop 
	client.disconnect() # disconnect

# These two listeners will handle the Sample Duration reset and the "real" events (such as keyboard ^C)
def on_sampleRateHandler(signo, _frame):
	logging.warning("SIGUSR1 gentle reset...\n" )
	# client.continueLoop continues to be true
	exit.set()

def on_quitHandler(signo, _frame):
	logging.warning("Interrupted by %d" % signo)
	logging.warning("shutting down..." )
	client.continueLoop = False
	exit.set()



if __name__ == '__main__':

	import signal

	#Register a Signal Handler for my sample reset function
	signal.signal(signal.SIGUSR1, on_sampleRateHandler )

	#Register 3 Signal Handlers (all to the same event handler function)
	for sig in ('TERM', 'HUP', 'INT' ):
		signal.signal(getattr(signal, 'SIG'+sig), on_quitHandler);

	main()
