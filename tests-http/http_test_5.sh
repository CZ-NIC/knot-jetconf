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

echo "--- POST new zone"
POST_DATA='{"zone": {"name": "newzone.cz", "class": "IN"}}'
URL="https://127.0.0.1:8443/restconf/data/dns-zones:zone-data"
curl -v --http2 -k --cert-type PEM -E $CLIENT_CERT -X POST -d "$POST_DATA" "$URL" 2>/dev/null

echo "--- PUT action"
POST_DATA='150'
URL="https://127.0.0.1:8443/restconf/data/dns-zones:zone-data/zone=pokus.cz,IN/default-ttl"
curl -v --http2 -k --cert-type PEM -E $CLIENT_CERT -X PUT -d "$POST_DATA" "$URL" 2>/dev/null

#echo "--- DEL rrl"
#URL="https://127.0.0.1:8443/restconf/data/dns-server:dns-server/server-options/response-rate-limiting"
#curl -v --http2 -k --cert-type PEM -E $CLIENT_CERT -X DELETE "$URL" 2>/dev/null

#echo "--- DEL example.com"
#POST_DATA=''
#URL="https://127.0.0.1:8443/restconf/data/dns-zones:zones/zone=example.com,IN"
#curl -v --http2 -k --cert-type PEM -E $CLIENT_CERT -X DELETE -d "$POST_DATA" "$URL" 2>/dev/null

echo "--- POST new zone SOA"
POST_DATA='{"SOA": {"mname": "dns1.newzone.cz","rname": "hostmaster.newzone.cz","serial": 20160622,"refresh": 200,"retry": 300,"expire": 400,"minimum": 500}}'
URL="https://127.0.0.1:8443/restconf/data/dns-zones:zone-data/zone=newzone.cz,IN"
curl -v --http2 -k --cert-type PEM -E $CLIENT_CERT -X POST -d "$POST_DATA" "$URL" 2>/dev/null

echo "--- POST new zone A"
POST_DATA='{"rrset": {"owner": "sub.newzone.cz", "type": "iana-dns-parameters:A", "rdata": [{"A": { "address": "192.168.100.100"}}]}}'
URL="https://127.0.0.1:8443/restconf/data/dns-zones:zone-data/zone=newzone.cz,IN"
curl -v --http2 -k --cert-type PEM -E $CLIENT_CERT -X POST -d "$POST_DATA" "$URL" 2>/dev/null

echo "--- conf-list"
URL="https://127.0.0.1:8443/restconf/operations/dns-server:conf-list"
curl -v --http2 -k --cert-type PEM -E $CLIENT_CERT -X POST "$URL" 2>/dev/null

echo "--- conf-commit"
URL="https://127.0.0.1:8443/restconf/operations/dns-server:conf-commit"
curl -v --http2 -k --cert-type PEM -E $CLIENT_CERT -X POST "$URL" 2>/dev/null

echo "--- GET zones"
URL="https://127.0.0.1:8443/restconf/data/dns-zones:zone-data/zone=newzone.cz,IN"
curl -v --http2 -k --cert-type PEM -E $CLIENT_CERT -X GET "$URL" 2>/dev/null
