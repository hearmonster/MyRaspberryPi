echo 'Please use pass phrase NETiRSS9BTYBx3HE for the certificate import from ./cert.pem in the conversion !'

openssl rsa -in ./GrovePi-device_certificate.pem -out credentials.key
openssl x509 -in ./GrovePi-device_certificate.pem -out credentials.crt
