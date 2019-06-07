#!/bin/bash

source ./http_conf

# Updating remote-server list,

PUT_DATA="@payload/remote-server-list-input.json"

echo "--- PUT new remote-server list configuration"
URL="${JC_URL}/restconf/data/cznic-dns-slave-server:dns-server/remote-server"
curl --http2 -k --cert-type PEM -E $CLIENT_CERT -X PUT -d "$PUT_DATA" "$URL"

echo "--- POST conf-commit"
URL="${JC_URL}/restconf/operations/jetconf:conf-commit"
curl --http2 -k --cert-type PEM -E $CLIENT_CERT -X POST "$URL"



