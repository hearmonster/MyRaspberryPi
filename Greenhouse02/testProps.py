from configparser import ConfigParser

config = ConfigParser()
propFile = 'testProps.properties'
config.read( propFile )

print( config['Landscape']['url'] )

deviceName = 'DN1'
my_deviceId = 'myDI1'
my_deviceAltId = 'myDAI1'

config['device'] = { 'deviceName': deviceName, 'deviceId': my_deviceId, 'deviceAltId': my_deviceAltId }

with open( propFile, 'w' ) as updatedConfigFile :
	config.write( updatedConfigFile )
