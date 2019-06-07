#!/bin/bash

source ./http_conf

POST_DATA='{"cznic-dns-slave-server:input": {}}'
URL="${JC_URL}/restconf/operations/cznic-dns-slave-server:stop-server"

echo "--- POST Operation 'stop-server'"
curl --http2 -k --cert-type PEM -E ${CLIENT_CERT} -X POST -d "$POST_DATA" "$URL"
