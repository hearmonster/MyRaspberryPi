echo 'Please use pass phrase mabCYhziZjCQy2Ky for the certificate import from ./Greenhouse_01-device-cert.pem in the conversion !'

openssl rsa -in ./Greenhouse_01-device-cert.pem -out Greenhouse_01-device-credentials.key
openssl x509 -in ./Greenhouse_01-device-cert.pem -out Greenhouse_01-device-credentials.crt
