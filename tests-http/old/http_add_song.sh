#!/bin/bash

CLIENT_CERT="/home/pspirek/sslclient/pavel_curl.pem"

echo "--- conf-start 1"
POST_DATA='{ "dns-server:input": {"name": "Edit 1"} }'
URL="https://195.113.220.112:8443/restconf/operations/dns-server:conf-start"
curl -v --http2 -k --cert-type PEM -E $CLIENT_CERT -X POST -d "$POST_DATA" "$URL" 2>/dev/null

echo "--- POST new song to playlist"
POST_DATA='{"song":{"id": "/example-jukebox:jukebox/library/artist[name=\"Foo Figthers\"]/album[name=\"Wasting Light\"]/song[name=\"Some new song\"]","index": 3}}'
URL="https://195.113.220.112:8443/restconf/data/example-jukebox:jukebox/playlist=Foo-One"
curl -v --http2 -k --cert-type PEM -E $CLIENT_CERT -X POST -d "$POST_DATA" "$URL" 2>/dev/null

echo "--- conf-list"
URL="https://195.113.220.112:8443/restconf/operations/dns-server:conf-list"
curl -v --http2 -k --cert-type PEM -E $CLIENT_CERT -X POST "$URL" 2>/dev/null

echo "--- conf-commit"
URL="https://195.113.220.112:8443/restconf/operations/dns-server:conf-commit"
curl -v --http2 -k --cert-type PEM -E $CLIENT_CERT -X POST "$URL" 2>/dev/null

echo "--- GET zones"
URL="https://195.113.220.112:8443/restconf/data/example-jukebox:jukebox/playlist=Foo-One"
curl -v --http2 -k --cert-type PEM -E $CLIENT_CERT -X GET "$URL" 2>/dev/null


