#!/bin/bash

source ./http_conf

echo "--- GET /restconf/data"
URL="${JC_URL}/restconf/data"
curl --http2 -k --cert-type PEM -E $CLIENT_CERT -X GET "$URL"

