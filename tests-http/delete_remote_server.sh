#!/bin/bash

source ./http_conf

if [ -z "$1" ]
then
    echo "Usage: $0 <server_name>"
else
    echo "--- DELETE $1 remote-server"
    URL="${JC_URL}/restconf/data/cznic-dns-slave-server:dns-server/remote-server=$1"
    curl --http2 -k --cert-type PEM -E $CLIENT_CERT -X DELETE "$URL"

    echo "--- POST conf-commit"
    URL="${JC_URL}/restconf/operations/jetconf:conf-commit"
    curl --http2 -k --cert-type PEM -E $CLIENT_CERT -X POST "$URL"
fi