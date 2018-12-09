#######################################################################################
#
# Connects to my Canary instance
#    (Note: MQTT uses "AltID" values,   RESTful API uses "ID" values)
#    Device (instance):
#             "Greenhouse_01-device"  AltID: "9f4677013c683b4e"
#    Sensor (instance):
#             "Greenhouse_01-sensor"  [Measure] Sensor AltID "9185f8d6bc70958a"
#    Capabilities:
#             "Greenhouse-capability" [Measure] Capability AltID "96e55acc21b17bee"
#                         Property: "Greenhouse_temp"         [Float]
#                         Property: "Greenhouse_humidity"     [Float]
#                         Property: "Greenhouse_light"        [Integer]
#                         Property: "Greenhouse_lampStatus"   [String]
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
#       Device:
#         AltID = 84dedf1bdb564bd3   (Name: My_Raspberry_Pi)
#         (3 x sensors)
#
#
#       MEASURES: Require the
#               1. The <Device AltID> (Topic)
#               2. The <AltID>  of each Sensor
#                       Sensor  Type    AltID                   Name
#                         #1  [Measure] b1ebcfa471f8c87e   (Name: DHTSensor01)
#                         #2  [Measure] abd3f4cc93b7fa50   (Name: LightSensor01)
#                         #3  [Command] D/K                (Name: Lamp01)
#                         #4  [Command] D/K                (Name: SampleDuration)
#               3. The <AltID>  of each Capability
#               4. The <Property Name> of each Property
#                         #1 Capability AltID = fb48689a05fdba88 (Name: GetTemperatureAndHumidity)
#                               #1a  Property Name = temperature
#                               #1a  Property Name = humidity
#                         #2 Capability AltID = 625a5e85958ea7b5 (Name: GetLightIntensity)
#                               #2a  Property Name = LightIntensity
#
#       COMMANDS: Require the <Device AltID> (Topic) and the <Property Name> of each Capability (Capability ID not required!?)
#         #1 Property Name = OnOff
#         #2 Property Name = sampleDuration
#
#
#capabilityAlternateId
#sCapabilityAltId
#
#sensorAlternateId
#sSensorAltId
#
#propertyName + SampleValue
#       Temp
#       Humidity

