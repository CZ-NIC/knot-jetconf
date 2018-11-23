#!/bin/bash

# Adds new zone "newzone.cz" to KNOT's configuration,
# then creates SOA record and "192.168.100.200" A record in it.

CLIENT_CERT="$HOME/sslclient/alois_curl.pem"

echo "--- POST new zone to configuration"
POST_DATA='{"dns-server:zone": {"domain": "newzone.cz"}}'
URL="https://127.0.0.1:8443/restconf/data/dns-server:dns-server/zones"
curl --http2 -k --cert-type PEM -E $CLIENT_CERT -X POST -d "$POST_DATA" "$URL"

echo "--- conf-commit"
URL="https://127.0.0.1:8443/restconf/operations/jetconf:conf-commit"
curl --http2 -k --cert-type PEM -E $CLIENT_CERT -X POST "$URL"

sleep 1

echo "--- OP KNOT begin-transaction"
URL="https://127.0.0.1:8443/restconf/operations/dns-zone-rpcs:begin-transaction"
curl --http2 -k --cert-type PEM -E $CLIENT_CERT -X POST "$URL"

echo "--- OP KNOT zone-set SOA"
POST_DATA="@zone-set-input-soa-newzonecz.json"
URL="https://127.0.0.1:8443/restconf/operations/dns-zone-rpcs:zone-set"
curl --http2 -k --cert-type PEM -E $CLIENT_CERT -X POST -d "$POST_DATA" "$URL"

echo "--- OP KNOT zone-set A"
POST_DATA="@zone-set-input-a-newzonecz.json"
URL="https://127.0.0.1:8443/restconf/operations/dns-zone-rpcs:zone-set"
curl --http2 -k --cert-type PEM -E $CLIENT_CERT -X POST -d "$POST_DATA" "$URL"

echo "--- OP KNOT commit-transaction"
URL="https://127.0.0.1:8443/restconf/operations/dns-zone-rpcs:commit-transaction"
curl --http2 -k --cert-type PEM -E $CLIENT_CERT -X POST "$URL"


