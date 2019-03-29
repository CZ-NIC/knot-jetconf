#!/bin/bash

# This will delete zone "newzone.cz" from KNOT's configuration

CLIENT_CERT="../conf/example-client_curl.pem"

echo "--- DEL newzone.cz from config"
URL="https://localhost:8443/restconf/data/cznic-dns-slave-server:dns-server/zones/zone=."
curl --http2 -k --cert-type PEM -E $CLIENT_CERT -X DELETE "$URL"

echo "--- conf-commit"
URL="https://localhost:8443/restconf/operations/jetconf:conf-commit"
curl --http2 -k --cert-type PEM -E $CLIENT_CERT -X POST "$URL"
