#-------------------------------------------------------------------------------
from configparser import ConfigParser
parser = ConfigParser()
tenantPropFile = '/home/pi/MyRaspberryPi/tenant.properties'
parser.read( tenantPropFile )


config_instance=parser['Landscape']['url']
config_user=parser['Landscape']['Username']
config_password=parser['Landscape']['Password']
config_crt_4_landscape=parser['Landscape']['CertBundle']

#-------------------------------------------------------------------------------
config_crt_4_landscape='/home/pi/MyRaspberryPi/canary_cp_iot_sap_BUNDLE.crt'
#-------------------------------------------------------------------------------
