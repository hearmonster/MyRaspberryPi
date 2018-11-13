config_broker_url='2f7241c1-8671-4591-9de0-8c64ed90e10e.canary.cp.iot.sap'
config_broker_port=8883
config_alternate_id_device='694b3a57781cad0e'      #declares Broker TOPIC.  ie 'GrovePi'
config_alternate_id_capability_up01='fb48689a05fdba88'   #ie 'GetTemperatureAndHumidity'
config_alternate_id_sensor='cbfdb4c7055403cb'  #ie 'DHT sensor'
config_crt_4_landscape='./canary_cp_iot_sap_BUNDLE.crt'
config_sleep_time=1800    #30 mins between samples
config_credentials_key='./credentials.key'
config_credentials_crt='./credentials.crt'

# ========================================================================
# imports

import sys
import time
import logging
import ssl

# as an additional / non standard module pre-condition: 
# install Paho MQTT lib e.g. from https://github.com/eclipse/paho.mqtt.python
import paho.mqtt.client as mqtt

import grovepi



# ========================================================================
# static configs

dht_sensor_port = 7     #D7 (Digital)
light_sensor_port = 1   #A1 (Analog)
#logging.basicConfig(level=logging.DEBUG)
iLEdPort = 4            #D4 (Digital)
bLEdState = True
print( "Port: ", iLEdPort, "State: ", bLEdState )
grovepi.digitalWrite( iLEdPort, bLEdState )

# ========================================================================
def on_connect_broker(client, userdata, flags, rc):
	if rc==0:
		print("connected OK Returned code=",rc)
	else:
		print("Bad connection - Returned code= ",rc)
	sys.stdout.flush()

def on_subscribe(client, obj, message_id, granted_qos):
	print('on_subscribe - message_id: ' + str(message_id) + ' / qos: ' + str(granted_qos))
	sys.stdout.flush()

def on_message(client, obj, msg):
	global bLEdState
	global iLEdPort
	# print('on_message - ' + msg.topic + ' ' + str(msg.qos))
	print('on_message - ' + msg.topic + ' ' + str(msg.qos) + ' ' + str(msg.payload))
	sys.stdout.flush()
	#Toggle LED on Port D4
	bLEdState = not bLEdState
	grovepi.digitalWrite( iLEdPort, bLEdState )
	print( "Port: ", iLEdPort, "State: ", bLEdState )
	sys.stdout.flush()
# === main starts here ===================================================

my_device=config_alternate_id_device
client=mqtt.Client(client_id=my_device, clean_session=True, userdata=None)
client.on_connect=on_connect_broker
client.on_subscribe=on_subscribe
client.on_message=on_message
client.tls_set(config_crt_4_landscape, certfile=config_credentials_crt, keyfile=config_credentials_key)
client.bConnectedFlag=False   #Custom property


#logger = logging.getLogger(__name__)
#client.enable_logger(logger)

print("Attempting connection to broker now...")
while not client.bConnectedFlag:
# {
	try:
		client.connect(config_broker_url, port=config_broker_port, keepalive=60)
		client.bConnectedFlag=True #set flag

	except (IOError,TypeError) as e:
		print("Not connected yet. (client.bConnectedFlag = ", client.bConnectedFlag, ")")
		sys.stdout.flush()
		time.sleep(10)
# } end while

print("Connected to broker.")
sys.stdout.flush()

my_publish_topic='measures/' + my_device
my_subscription_topic='commands/' + my_device
client.subscribe(my_subscription_topic, 0)

client.loop_start()

time.sleep( 10 )

while True:
# {
	print('in main loop')
	sys.stdout.flush()

	try:
		[ temp, hum ] = grovepi.dht( dht_sensor_port, 0 )
		#print( "temp: ",temp, "C\thumidity: ",hum,"%" )
		payload='{ "capabilityAlternateId": "fb48689a05fdba88", "sensorAlternateId": "cbfdb4c7055403cb", "measures": [{"temperature": "' + str(temp) + '" },{"humidity": "' + str(hum) + '" }] }'
		result=client.publish(my_publish_topic, payload, qos=0)
		#print("published for capability >>>GetTemperatureAndHumidity<<<  payload: " + payload + "   with result: " + str(result))
		sys.stdout.flush()

		time.sleep(5)   # delay workaround for Bug:  https://forum.dexterindustries.com/t/dht-sensor-vs-light-sensor/904/2
		light_sensor_value = grovepi.analogRead( light_sensor_port )
		print( "light: ", light_sensor_value )
		payload='{ "capabilityAlternateId": "e9df11f2c54275f4", "sensorAlternateId": "e1a42e1a61e3a5ae", "measures": [{"sample": "' + str( light_sensor_value ) + '" }] }'
		result=client.publish(my_publish_topic, payload, qos=0)
		#print("published for capability >>>GetLight<<< payload: " + payload + "    with result: " + str(result))
		sys.stdout.flush()

	except (IOError,TypeError) as e:
		print( "Error" )

	time.sleep(config_sleep_time)
# } end while
