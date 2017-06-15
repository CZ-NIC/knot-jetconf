#!/bin/bash

# This will delete zone "newzone.cz" from KNOT's configuration

CLIENT_CERT="/home/pspirek/sslclient/pavel_curl.pem"

echo "--- conf-start"
URL="https://127.0.0.1:8443/restconf/operations/jetconf:conf-start"
curl --http2 -k --cert-type PEM -E $CLIENT_CERT -X POST "$URL"

echo "--- DEL newzone.cz from config"
URL="https://127.0.0.1:8443/restconf/data/dns-server:dns-server/zones/zone=newzone.cz"
curl --http2 -k --cert-type PEM -E $CLIENT_CERT -X DELETE "$URL"

echo "--- conf-commit"
URL="https://127.0.0.1:8443/restconf/operations/jetconf:conf-commit"
curl --http2 -k --cert-type PEM -E $CLIENT_CERT -X POST "$URL"
