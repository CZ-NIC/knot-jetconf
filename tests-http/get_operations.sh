#!/bin/bash

source ./http_conf

URL="${JC_URL}/restconf/operations/"

echo "--- GET list of operations
curl --http2 -k --cert-type PEM -E ${CLIENT_CERT} -X GET "$URL"
