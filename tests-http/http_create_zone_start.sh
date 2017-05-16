#!/bin/bash

CLIENT_CERT="/home/pspirek/sslclient/pavel_curl.pem"

echo "--- begin-transaction"
URL="https://127.0.0.1:8443/restconf/operations/dns-zone-rpcs:begin-transaction"
curl --http2 -k --cert-type PEM -E $CLIENT_CERT -X POST "$URL"

echo "--- conf-set"
POST_DATA="@zone-set-input-2.json"
URL="https://127.0.0.1:8443/restconf/operations/dns-zone-rpcs:zone-set"
curl --http2 -k --cert-type PEM -E $CLIENT_CERT -X POST -d "$POST_DATA" "$URL"

read a

echo "--- conf-unset"
POST_DATA="@zone-unset-input.json"
URL="https://127.0.0.1:8443/restconf/operations/dns-zone-rpcs:zone-unset"
curl --http2 -k --cert-type PEM -E $CLIENT_CERT -X POST -d "$POST_DATA" "$URL"

read a

echo "--- conf-unset 2"
POST_DATA="@zone-unset-input-2.json"
URL="https://127.0.0.1:8443/restconf/operations/dns-zone-rpcs:zone-unset"
curl --http2 -k --cert-type PEM -E $CLIENT_CERT -X POST -d "$POST_DATA" "$URL"

read a

echo "--- abort-transaction"
URL="https://127.0.0.1:8443/restconf/operations/dns-zone-rpcs:abort-transaction"
curl --http2 -k --cert-type PEM -E $CLIENT_CERT -X POST "$URL"


