#!/bin/bash

# This will rewrite "example.com" zone configuration

CLIENT_CERT="$HOME/sslclient/alois_curl.pem"

echo "--- PUT data"
PUT_DATA="@conf-input-replace-examplecom.json"
URL="https://127.0.0.1:8443/restconf/data/dns-server:dns-server/zones/zone=example.com"
curl --http2 -k --cert-type PEM -E $CLIENT_CERT -X PUT -d "$PUT_DATA" "$URL"

echo "--- conf-commit"
URL="https://127.0.0.1:8443/restconf/operations/jetconf:conf-commit"
curl --http2 -k --cert-type PEM -E $CLIENT_CERT -X POST "$URL" 2>/dev/null

