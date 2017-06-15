#!/bin/bash

# This will modify "query-module" item in "example.com", by overwriting the whole zone configuration.

CLIENT_CERT="/home/pspirek/sslclient/pavel_curl.pem"

echo "--- conf-start"
URL="https://127.0.0.1:8443/restconf/operations/dns-server:conf-start"
curl --http2 -k --cert-type PEM -E $CLIENT_CERT -X POST "$URL"

echo "--- PUT data"
PUT_DATA='{"domain": "example.com","template": "default","any-to-tcp": false,"access-control-list": ["acl_local"],"query-module": [{"type": "knot-dns:synth-record","name": "test1"},{"type": "knot-dns:synth-record","name": "test2"}]}'
URL="https://127.0.0.1:8443/restconf/data/dns-server:dns-server/zones/zone=example.com"
curl --http2 -k --cert-type PEM -E $CLIENT_CERT -X PUT -d "$PUT_DATA" "$URL"

echo "--- conf-commit"
URL="https://127.0.0.1:8443/restconf/operations/dns-server:conf-commit"
curl --http2 -k --cert-type PEM -E $CLIENT_CERT -X POST "$URL" 2>/dev/null

