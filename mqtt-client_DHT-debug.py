config_broker='2f7241c1-8671-4591-9de0-8c64ed90e10e.canary.cp.iot.sap'
config_alternate_id_device='694b3a57781cad0e'      #declares Broker TOPIC.  ie 'GrovePi'
config_alternate_id_capability_up01='fb48689a05fdba88'   #ie 'GetTemperatureAndHumidity'
config_alternate_id_sensor='cbfdb4c7055403cb'  #ie 'DHT sensor'
config_crt_4_landscape='./canary_cp_iot_sap_BUNDLE.crt'

import sys
import time
import logging
import ssl

logging.basicConfig(level=logging.DEBUG)

# as an additional / non standard module pre-condition: 
# install Paho MQTT lib e.g. from https://github.com/eclipse/paho.mqtt.python
import paho.mqtt.client as mqtt

from grovepi import *
dht_sensor_port = 7

# ========================================================================
def on_connect_broker(client, userdata, flags, rc):
	print('Connected to MQTT broker with result code: ' + str(rc))
	sys.stdout.flush()

def on_subscribe(client, obj, message_id, granted_qos):
	print('on_subscribe - message_id: ' + str(message_id) + ' / qos: ' + str(granted_qos))
	sys.stdout.flush()

def on_message(client, obj, msg):
	# print('on_message - ' + msg.topic + ' ' + str(msg.qos))
	print('on_message - ' + msg.topic + ' ' + str(msg.qos) + ' ' + str(msg.payload))
	sys.stdout.flush()
# ========================================================================

# === main starts here ===================================================

config_credentials_key='./credentials.key'
config_credentials_crt='./credentials.crt'

broker=config_broker
broker_port=8883

my_device=config_alternate_id_device
#client=mqtt.Client(client_id=my_device)
client=mqtt.Client(client_id=my_device, clean_session=True, userdata=None)
client.on_connect=on_connect_broker
client.on_subscribe=on_subscribe
client.on_message=on_message

logger = logging.getLogger(__name__)
client.enable_logger(logger)

client.tls_set(config_crt_4_landscape, certfile=config_credentials_crt, keyfile=config_credentials_key)

not_connected=True
while not_connected:
# {
	try:
		#client.connect(broker, broker_port, 60)
		client.connect(broker, port=broker_port, keepalive=60)
		not_connected=False
	except:
		print("not connected yet")
		sys.stdout.flush()
		time.sleep(5)
# } while

print("connected to broker now")
sys.stdout.flush()

my_publish_topic='measures/' + my_device
my_subscription_topic='commands/' + my_device
client.subscribe(my_subscription_topic, 0)

client.loop_start()

sleep_time=10
time.sleep(sleep_time)

while True:
	print('in main loop')
	sys.stdout.flush()

	time.sleep(sleep_time)
	try:
		[ temp, hum ] = dht( dht_sensor_port, 0 )
		#print( "temp: ",temp, "C\thumidity: ",hum,"%" )
		payload='{ "capabilityAlternateId": "fb48689a05fdba88", "sensorAlternateId": "cbfdb4c7055403cb", "measures": [{"temperature": "' + str(temp) + '" },{"humidity": "' + str(hum) + '" }] }'
		print( payload )
		#payload='{ "capabilityAlternateId" : "' + config_alternate_id_capability_up01 + '", "measures" : [[ "value for p01_up01", "value for p02_up01" ]], "sensorAlternateId":"' + config_alternate_id_sensor + '" }'
		result=client.publish(my_publish_topic, payload, qos=0)
		print("published for capability up01 with result: " + str(result))
		sys.stdout.flush()
	except (IOError,TypeError) as e:
		print( "Error" )

