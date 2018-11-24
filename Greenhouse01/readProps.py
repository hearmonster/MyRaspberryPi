from configparser import ConfigParser

parser = ConfigParser()
propFile = 'Greenhouse_02_device.properties'
parser.read( propFile )

find_sections = ['device', 'sensor', 'sensorType', 'capability']
#print( parser.get( propFile, 'deviceId' ) )  
print( parser['device']['deviceId'] )
