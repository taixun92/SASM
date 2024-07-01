openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -config "{{ * please input path where file exist * }}\openssl.cnf"

PEM pass phrase:sasm

Country Name (2 letter code) [AU]:KR
State or Province Name (full name) [Some-State]:Seoul
Locality Name (eg, city) []:
Organization Name (eg, company) [Internet Widgits Pty Ltd]:SASM
Organizational Unit Name (eg, section) []:
Common Name (e.g. server FQDN or YOUR name) []:
Email Address []: