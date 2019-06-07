#!/bin/bash

source ./http_conf

PUT_DATA="@payload/zone-list-input.json"

echo "--- PUT new zone list to configuration"
URL="${JC_URL}/restconf/data/cznic-dns-slave-server:dns-server/zones/zone"
curl --http2 -k --cert-type PEM -E $CLIENT_CERT -X PUT -d "$PUT_DATA" "$URL"

echo "--- POST conf-commit"
URL="${JC_URL}/restconf/operations/jetconf:conf-commit"
curl --http2 -k --cert-type PEM -E $CLIENT_CERT -X POST "$URL"



