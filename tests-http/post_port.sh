#!/bin/bash

source ./http_conf

# Updating zones list,

POST_DATA="@payload/port.json"
SERVER=$1

if [ -z "$SERVER" ]
then
    echo "Missing argument: use name of remote-server as argument"
else
    echo "--- POST port to ${SERVER} remote-server configuration"
    URL="${JC_URL}/restconf/data/cznic-dns-slave-server:dns-server/remote-server=${SERVER}/remote"
    curl --http2 -k --cert-type PEM -E $CLIENT_CERT -X POST -d "$POST_DATA" "$URL"

    echo "--- POST conf-commit"
    URL="${JC_URL}/restconf/operations/jetconf:conf-commit"
    curl --http2 -k --cert-type PEM -E $CLIENT_CERT -X POST "$URL"
fi


