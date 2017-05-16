#!/bin/bash

CLIENT_CERT="/home/pspirek/sslclient/pavel_curl.pem"

echo "--- conf-start 1"
POST_DATA='{ "dns-server:input": {"name": "Edit 1", "options": "config"} }'
URL="https://127.0.0.1:8443/restconf/operations/dns-server:conf-start"
curl -v --http2 -k --cert-type PEM -E $CLIENT_CERT -X POST -d "$POST_DATA" "$URL" 2>/dev/null

echo "--- PUT data"
POST_DATA='{"domain": "example.com","template": "default","any-to-tcp": false,"access-control-list": ["acl_local"],"query-module": [{"type": "knot-dns:synth-record","name": "test1"},{"type": "knot-dns:synth-record","name": "test2"}]}'
URL="https://127.0.0.1:8443/restconf/data/dns-server:dns-server/zones/zone=example.com"
curl -v --http2 -k --cert-type PEM -E $CLIENT_CERT -X PUT -d "$POST_DATA" "$URL" 2>/dev/null

echo "--- conf-commit"
URL="https://127.0.0.1:8443/restconf/operations/dns-server:conf-commit"
curl -v --http2 -k --cert-type PEM -E $CLIENT_CERT -X POST "$URL" 2>/dev/null

