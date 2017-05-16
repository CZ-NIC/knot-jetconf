#!/bin/bash

CLIENT_CERT="/home/pspirek/sslclient/pavel_curl.pem"

echo "--- conf-start 1"
POST_DATA='{ "jetconf:input": {"name": "Edit 1", "options": "config"} }'
URL="https://127.0.0.1:8443/restconf/operations/jetconf:conf-start"
curl --http2 -k --cert-type PEM -E $CLIENT_CERT -X POST -d "$POST_DATA" "$URL"

echo "--- POST new zone"
POST_DATA='{"dns-server:zone": {"domain": "newzone.cz"}}'
URL="https://127.0.0.1:8443/restconf/data/dns-server:dns-server/zones"
curl --http2 -k --cert-type PEM -E $CLIENT_CERT -X POST -d "$POST_DATA" "$URL"

echo "--- conf-commit"
URL="https://127.0.0.1:8443/restconf/operations/jetconf:conf-commit"
curl --http2 -k --cert-type PEM -E $CLIENT_CERT -X POST "$URL"

sleep 2

echo "--- begin-transaction"
URL="https://127.0.0.1:8443/restconf/operations/dns-zone-rpcs:begin-transaction"
curl --http2 -k --cert-type PEM -E $CLIENT_CERT -X POST "$URL"

echo "--- conf-set"
POST_DATA="@zone-set-input.json"
URL="https://127.0.0.1:8443/restconf/operations/dns-zone-rpcs:zone-set"
curl --http2 -k --cert-type PEM -E $CLIENT_CERT -X POST -d "$POST_DATA" "$URL"

echo "--- conf-set"
POST_DATA="@zone-set-input-a.json"
URL="https://127.0.0.1:8443/restconf/operations/dns-zone-rpcs:zone-set"
curl --http2 -k --cert-type PEM -E $CLIENT_CERT -X POST -d "$POST_DATA" "$URL"

echo "--- commit-transaction"
URL="https://127.0.0.1:8443/restconf/operations/dns-zone-rpcs:commit-transaction"
curl --http2 -k --cert-type PEM -E $CLIENT_CERT -X POST "$URL"


