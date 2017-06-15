#!/bin/bash

# This will remove A record 192.0.2.3 in zone "example.com",
# and write a new A record 50.50.50.50 instead.

CLIENT_CERT="/home/pspirek/sslclient/pavel_curl.pem"

echo "--- OP KNOT begin-transaction"
URL="https://127.0.0.1:8443/restconf/operations/dns-zone-rpcs:begin-transaction"
curl --http2 -k --cert-type PEM -E $CLIENT_CERT -X POST "$URL"

echo "--- OP KNOT conf-set A 50.50.50.50"
POST_DATA="@zone-set-input-a-examplecom.json"
URL="https://127.0.0.1:8443/restconf/operations/dns-zone-rpcs:zone-set"
curl --http2 -k --cert-type PEM -E $CLIENT_CERT -X POST -d "$POST_DATA" "$URL"

echo "--- OP KNOT conf-unset A 192.0.2.3"
POST_DATA="@zone-unset-input-a-examplecom.json"
URL="https://127.0.0.1:8443/restconf/operations/dns-zone-rpcs:zone-unset"
curl --http2 -k --cert-type PEM -E $CLIENT_CERT -X POST -d "$POST_DATA" "$URL"

echo "--- OP KNOT commit-transaction"
URL="https://127.0.0.1:8443/restconf/operations/dns-zone-rpcs:commit-transaction"
curl --http2 -k --cert-type PEM -E $CLIENT_CERT -X POST "$URL"


