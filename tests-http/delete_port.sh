#!/bin/bash

source ./http_conf

# Updating zones list,

if [ -z "$1" ]
then
    echo "Usage: $1 <remote_server_name>"
else
    echo "--- DELETE port from ${SERVER} server configuration"
    URL="${JC_URL}/restconf/data/cznic-dns-slave-server:dns-server/remote-server=$1/remote/port"
    curl --http2 -k --cert-type PEM -E $CLIENT_CERT -X DELETE "$URL"

    echo "--- POST conf-commit"
    URL="${JC_URL}/restconf/operations/jetconf:conf-commit"
    curl --http2 -k --cert-type PEM -E $CLIENT_CERT -X POST "$URL"
fi


