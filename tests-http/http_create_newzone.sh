#!/bin/bash

# Adds new zone "newzone.cz" to KNOT's configuration

CLIENT_CERT="/home/pspirek/sslclient/pavel_curl.pem"

echo "--- POST new zone to configuration"
POST_DATA='{"dns-server:zone": {"domain": "newzone.cz", "file": "/tmp/somewhere/newzone.cz.zone"}}'
URL="https://127.0.0.1:8443/restconf/data/dns-server:dns-server/zones"
curl --http2 -k --cert-type PEM -E $CLIENT_CERT -X POST -d "$POST_DATA" "$URL"

echo "--- conf-commit"
URL="https://127.0.0.1:8443/restconf/operations/jetconf:conf-commit"
curl --http2 -k --cert-type PEM -E $CLIENT_CERT -X POST "$URL"


