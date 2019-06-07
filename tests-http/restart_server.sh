#!/bin/bash

source ./http_conf

URL="${JC_URL}/restconf/operations/cznic-dns-slave-server:restart-server"
POST_DATA='{"cznic-dns-slave-server:input": {}}'

echo "--- POST Operation 'restart-server'"

curl --http2 -k --cert-type PEM -E ${CLIENT_CERT} -X POST -d "$POST_DATA" "$URL"
