#######################################################################################
#
# Connects to my Canary instance 
#    (Note: MQTT uses "AltID" values,   RESTful API uses "ID" values)
#    Device:
#             "Greenhouse01"  AltID: "b34745c497cda49b"
#    Sensor:
#             "Greenhouse1_sensor1"  [Measure] Sensor AltID "2c93b574387374ea"
#    Capabilities:
#             "greenhouse_capability"     [Measure] Capability AltID "e93ec4edb28720e3"
#                         Property: "temperature" [Integer]
#                         Property: "humidity"    [Integer]
#                         Property: "light"       [Integer]
#
# Modified payload (one element with three keys, instead of three elements each with one key) - compatible with IoT AE
#
# Configurable logging implemented (writes to std out. Separate log file output possible, but commented out)
#
# Captures DHT and Light (with a two second delay between the two samples to workaround locking the I/O bus)
#   * Pressing the button while the DHT samples are being read, will invoke an override that will
#     increase the temperature by one degree each cycle
#   * Releasing the button will gradually reduce the temp value back to it's true value
#     (the override will decrease by 1 each cycle, until it returns back to zero - it won't go below zero)
#
# The initial state of the LED is lit, although it is configurable - see "Commands" below.
#
# Accepts Commands - parses out the command and payload
#       to toggle the LED - command: "OnOff",
#               * accepts TRUE/FALSE (case insenstive)
#                 fully implemented example illustrated by running the 'originate-command_OnOFF.py' script
#       to reset the sample duration - command "sampleDuration"
#               * accepts INT (seconds) either wrapped in quotes or not
#               * interupts the current wait immediately,
#                 (implemented using Python Events and OS Signal Interupts)
#                 fully implemented example illustrated by running the 'originate-command_sampleDuration.py' script
#
# Shuts down gracefully:
#   * disconnects from MQTT Broker
#   * Turns off the LED
#
#

config_broker_url='2f7241c1-8671-4591-9de0-8c64ed90e10e.canary.cp.iot.sap'
config_broker_port=8883
config_alternate_id_Device='b34745c497cda49b'      #declares Broker TOPIC.  ie 'GrovePi'
config_alternate_id_Sensor = '2c93b574387374ea'
config_alternate_id_Capability = 'e93ec4edb28720e3'
config_crt_4_landscape='./canary_cp_iot_sap_BUNDLE.crt'
config_sleep_time=30	#Sample Rate (in seconds).  e.g. 1800 => 30 mins between samples
config_credentials_key='./greenhouse01-device-credentials.key'
config_credentials_crt='./greenhouse01-device-credentials.crt'

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
logging.basicConfig( level=logging.DEBUG )  #DEBUG, INFO, WARNING
iLEdPort = 4            #D4 (Digital)
iButtonPort = 8         #D8 (Digital)
iOverride = 0

# ========================================================================
def setLed( sOnOff_command_argument ):
	# Note: Takes a STRING (not a BOOL!) as an argument

	logging.info( 'sOnOff_command_argument: ' + sOnOff_command_argument)
	#Advice is to never attempt a cast to Bool in python!  
	#	https://stackoverflow.com/questions/715417/converting-from-a-string-to-boolean-in-python

	client.bLEdState = isTrue( sOnOff_command_argument )

	#Toggle LED on Port D4
	#client.bLEdState = not client.bLEdState
	grovepi.digitalWrite( iLEdPort, client.bLEdState )
	logging.info( "LED Port: " + str( iLEdPort ) + "\tState: " + str( client.bLEdState ) + "\n" )


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
	[ fTemp, fHumidity ] = grovepi.dht( iDHtSensorPort, 0 )
	logging.info( "Temp reading: " + str( fTemp ) + "C\tHumidity reading: " + str( fHumidity ) + "%" )
	client.fSample_Temp = fTemp + client.iOverride  #always safe to add it whether it's zero or non-zero
	client.fSample_Humidity = fHumidity
	if client.iOverride > 0:
		logging.info( "Override invoked. Current Override value: " + str( client.iOverride ) + "\tNew temp value: " + str( client.fSample_Temp) )
	logging.debug( "'client' Object settings for Temp: " + str( client.fSample_Temp ) + " and Humidity: " + str( client.fSample_Humidity ) )
               
def getLightReading():
	logging.info( "Obtaining Light reading..." )
	iLightSensorValue = grovepi.analogRead( iLightSensorPort )
	logging.info( "light reading: " + str( iLightSensorValue ) )
	client.iSample_Light = iLightSensorValue
	logging.debug( "'client' Object settings for Light: " + str( client.iSample_Light ) )


def calculateOverride():
	isButtonPressed = grovepi.digitalRead( iButtonPort )
	if isButtonPressed:
		client.iOverride = client.iOverride + 1
		logging.info( "Button depressed current state: TRUE   Override has increased to: " + str( client.iOverride ) + "\n" )
	else:
		logging.debug( "Button depressed current state: FALSE" )
		if  client.iOverride == 0:
			logging.debug( "Override value cannot fall below zero")
		else:
			client.iOverride = client.iOverride - 1
			logging.info( "Override value invoked but decreased to: " + str( client.iOverride ) + "\n" )

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

my_device=config_alternate_id_Device
client=mqtt.Client(client_id=my_device, clean_session=True, userdata=None)
client.on_connect=on_connect_brokerHandler
client.on_subscribe=on_subscribeHandler
client.on_message=on_messageHandler
client.tls_set(config_crt_4_landscape, certfile=config_credentials_crt, keyfile=config_credentials_key)
client.bConnectedFlag=False   #Custom property
client.bLEdState = True
client.iSleepTime = config_sleep_time
client.continueLoop = True
client.iOverride = iOverride
client.fSample_Temp = 0
client.fSample_Humidity = 0
client.iSample_Light = 0

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
				calculateOverride()

				getDhtReadings()

				time.sleep(2)   # delay workaround for Bug:  https://forum.dexterindustries.com/t/dht-sensor-vs-light-sensor/904/2

				getLightReading()
				sPayload='{ "capabilityAlternateId": "' + config_alternate_id_Capability + '", "sensorAlternateId": "' + config_alternate_id_Sensor + '", "measures": [{"gh_temp": "' + str( client.fSample_Temp ) + '","gh_humidity": "' + str( client.fSample_Humidity ) + '","gh_light": "' + str( client.iSample_Light ) + '" }] }'
				logging.debug("Payload: " + str(sPayload) + "\n")
				sResult=client.publish(my_publish_topic, sPayload, qos=0)
				logging.info("result of publish for capability >>>greenhouse_capability<<<  : " + str(sResult) + "\n")

			except (IOError,TypeError) as e:
				logging.error( "Error" )

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
	logging.warning("SIGUSR1 gentle reset...\n" )
	# client.continueLoop continues to be true
	exit.set()

def on_quitHandler(signo, _frame):
	# sets the 'client.continueLoop' property to False, then returns control back to the main() loop
	# The ' exit.set()' below will trigger an immediate exit from the loop
	# The loop will see the 'client.continueLoop' property has been set to False and will "refuse" to rerun the loop
	# resulting in the clean up commands being run just before main() terminates
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
