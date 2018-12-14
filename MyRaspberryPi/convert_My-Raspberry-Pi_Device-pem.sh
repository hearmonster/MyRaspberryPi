
openssl rsa  -in ./My-Raspberry-Pi-device_certificate.pem -out My-Raspberry-Pi_device_credentials.key
openssl x509 -in ./My-Raspberry-Pi-device_certificate.pem -out My-Raspberry-Pi_device_credentials.crt
