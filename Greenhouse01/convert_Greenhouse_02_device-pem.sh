echo 'Please use pass phrase zl45Ia2DT4WANoo0 for the certificate import from ./Greenhouse_02_device-cert.pem in the conversion !'

openssl rsa -in ./Greenhouse_02_device-cert.pem -out Greenhouse_02_device-credentials.key
openssl x509 -in ./Greenhouse_02_device-cert.pem -out Greenhouse_02_device-credentials.crt
