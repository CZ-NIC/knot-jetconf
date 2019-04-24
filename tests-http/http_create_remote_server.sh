#!/bin/bash

# Adds new remote-server "exrec" to KNOT's configuration,

CLIENT_CERT="../conf/example-client_curl.pem"
POST_DATA="@payload/create-zone-input.json"

echo "--- POST new remote-server to configuration"
URL="https://localhost:8443/restconf/data/cznic-dns-slave-server:dns-server"
curl --http2 -k --cert-type PEM -E $CLIENT_CERT -X PUT -d "$POST_DATA" "$URL"

echo "--- conf-commit"
URL="https://localhost:8443/restconf/operations/jetconf:conf-commit"
curl --http2 -k --cert-type PEM -E $CLIENT_CERT -X POST "$URL"



