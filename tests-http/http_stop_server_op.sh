#!/bin/bash

# rpc operation stop server

CLIENT_CERT="../conf/example-client_curl.pem"
POST_DATA="@payload/reload-server-input.json"
URL="https://localhost:8443/restconf/operations/cznic-dns-slave-server:stop-server"

echo "--- Operation 'stop-server'"
curl --http2 -k --cert-type PEM -E ${CLIENT_CERT} -X POST -d "$POST_DATA" "$URL"
