#!/bin/bash

# rpc operation restart server

CLIENT_CERT="../conf/example-client_curl.pem"
POST_DATA="@payload/reload-server-input.json"
URL="https://localhost:8443/restconf/operations/cznic-dns-slave-server:restart-server"

echo "--- Operation 'restart-server'"
curl --http2 -k --cert-type PEM -E ${CLIENT_CERT} -X POST -d "$POST_DATA" "$URL"
