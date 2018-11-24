echo 'Please use pass phrase E0drXkKbmeTEmaci for the certificate import from ./Greenhouse_02_Device-cert.pem in the conversion !'

openssl rsa -in ./Greenhouse_02_Device-cert.pem -out Greenhouse_02_Device-credentials.key
openssl x509 -in ./Greenhouse_02_Device-cert.pem -out Greenhouse_02_Device-credentials.crt
