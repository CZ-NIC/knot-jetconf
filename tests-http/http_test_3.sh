#!/bin/bash

CLIENT_CERT="/home/pspirek/sslclient/pavel_curl.pem"

echo "--- conf-start 1"
POST_DATA='{ "dns-server:input": {"name": "Edit 1"} }'
URL="https://127.0.0.1:8443/restconf/operations/dns-server:conf-start"
curl -v --http2 -k --cert-type PEM -E $CLIENT_CERT -X POST -d "$POST_DATA" "$URL" 2>/dev/null

#echo "--- PUT runtimedir"
#POST_DATA='"/muj/dir"'
#URL="https://127.0.0.1:8443/restconf/data/dns-server:dns-server/server-options/filesystem-paths/run-time-dir"
#curl -v --http2 -k --cert-type PEM -E $CLIENT_CERT -X PUT -d "$POST_DATA" "$URL" 2>/dev/null

#echo "--- DEL rrl"
#URL="https://127.0.0.1:8443/restconf/data/dns-server:dns-server/server-options/response-rate-limiting"
#curl -v --http2 -k --cert-type PEM -E $CLIENT_CERT -X DELETE "$URL" 2>/dev/null

echo "--- PUT error"
POST_DATA='"error"'
URL="https://127.0.0.1:8443/restconf/data/dns-server:dns-server/knot-dns:log=syslog/any"
curl -v --http2 -k --cert-type PEM -E $CLIENT_CERT -X PUT -d "$POST_DATA" "$URL" 2>/dev/null

echo "--- POST zone"
POST_DATA='{"zone":"info"}'
URL="https://127.0.0.1:8443/restconf/data/dns-server:dns-server/knot-dns:log=syslog"
curl -v --http2 -k --cert-type PEM -E $CLIENT_CERT -X POST -d "$POST_DATA" "$URL" 2>/dev/null

#echo "--- DEL rrl"
#URL="https://127.0.0.1:8443/restconf/data/dns-server:dns-server/server-options/response-rate-limiting"
#curl -v --http2 -k --cert-type PEM -E $CLIENT_CERT -X DELETE "$URL" 2>/dev/null

echo "--- conf-commit"
URL="https://127.0.0.1:8443/restconf/operations/dns-server:conf-commit"
curl -v --http2 -k --cert-type PEM -E $CLIENT_CERT -X POST "$URL" 2>/dev/null

echo "--- GET zones"
URL="https://127.0.0.1:8443/restconf/data/dns-server:dns-server/knot-dns:log"
curl -v --http2 -k --cert-type PEM -E $CLIENT_CERT -X GET "$URL" 2>/dev/null
