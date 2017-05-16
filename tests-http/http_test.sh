#!/bin/bash

CLIENT_CERT="/home/pspirek/sslclient/pavel_curl.pem"

echo "--- conf-start 1"
POST_DATA='{ "dns-server:input": {"name": "zone editing 1"} }'
URL="https://127.0.0.1:8443/restconf/operations/dns-server:conf-start"
curl -v --http2 -k --cert-type PEM -E $CLIENT_CERT -X POST -d "$POST_DATA" "$URL" 2>/dev/null

echo "--- conf-start 2"
POST_DATA='{ "dns-server:input": {"name": "zone editing 2"} }'
URL="https://127.0.0.1:8443/restconf/operations/dns-server:conf-start"
curl -v --http2 -k --cert-type PEM -E $CLIENT_CERT -X POST -d "$POST_DATA" "$URL" 2>/dev/null

echo "--- conf-list"
URL="https://127.0.0.1:8443/restconf/operations/dns-server:conf-list"
curl -v --http2 -k --cert-type PEM -E $CLIENT_CERT -X POST "$URL" 2>/dev/null

echo "--- conf-drop"
URL="https://127.0.0.1:8443/restconf/operations/dns-server:conf-drop"
curl -v --http2 -k --cert-type PEM -E $CLIENT_CERT -X POST "$URL" 2>/dev/null

echo "--- conf-list"
URL="https://127.0.0.1:8443/restconf/operations/dns-server:conf-list"
curl -v --http2 -k --cert-type PEM -E $CLIENT_CERT -X POST "$URL" 2>/dev/null

echo "--- POST myzone.com"
POST_DATA='{ "zone": {"domain": "myzone.com"} }'
URL="https://127.0.0.1:8443/restconf/data/dns-server:dns-server/zones"
curl -v --http2 -k --cert-type PEM -E $CLIENT_CERT -X POST -d "$POST_DATA" "$URL" 2>/dev/null

echo "--- conf-list"
URL="https://127.0.0.1:8443/restconf/operations/dns-server:conf-list"
curl -v --http2 -k --cert-type PEM -E $CLIENT_CERT -X POST "$URL" 2>/dev/null

echo "--- GET zones"
URL="https://127.0.0.1:8443/restconf/data/dns-server:dns-server/zones/zone"
curl -v --http2 -k --cert-type PEM -E $CLIENT_CERT -X GET "$URL" 2>/dev/null

read
echo "--- conf-commit"
URL="https://127.0.0.1:8443/restconf/operations/dns-server:conf-commit"
curl -v --http2 -k --cert-type PEM -E $CLIENT_CERT -X POST "$URL" 2>/dev/null

echo "--- conf-list"
URL="https://127.0.0.1:8443/restconf/operations/dns-server:conf-list"
curl -v --http2 -k --cert-type PEM -E $CLIENT_CERT -X POST "$URL" 2>/dev/null

echo "--- GET zones"
URL="https://127.0.0.1:8443/restconf/data/dns-server:dns-server/zones/zone"
curl -v --http2 -k --cert-type PEM -E $CLIENT_CERT -X GET "$URL" 2>/dev/null

