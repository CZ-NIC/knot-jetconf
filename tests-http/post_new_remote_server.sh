#!/bin/bash

source ./http_conf

if [ -z "$1" ]
then
	echo "Usage: $0 <new-remote-server.json>"
else
	POST_DATA="@$1"

	echo "--- POST new remote-server to configuration"
	URL="${JC_URL}/restconf/data/cznic-dns-slave-server:dns-server"
	curl --http2 -k --cert-type PEM -E $CLIENT_CERT -X POST -d "$POST_DATA" "$URL"

	echo "--- POST conf-commit"
	URL="${JC_URL}/restconf/operations/jetconf:conf-commit"
	curl --http2 -k --cert-type PEM -E $CLIENT_CERT -X POST "$URL"
fi


