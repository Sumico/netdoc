#!/bin/bash

REPO="/Users/andrea/Documents/netdoc.all/devices/"
SITE="default"
TMP=$(mktemp -t netdoc_)

curl -k -s -X POST -d "{\"id\":\"default\"}" -H 'Content-type: application/json' "http://127.0.0.1:5000/api/v1/sites"

for VLAN in $(cat ${REPO}/*/show_vlan | grep active | awk '{print $1 "," $2}' | sort -un); do
  VLAN_ID=$(echo $VLAN | cut -d',' -f1)
  VLAN_NAME=$(echo $VLAN | cut -d',' -f2)
  curl -k -s -X POST -d "{\"id\":${VLAN_ID},\"site_id\":\"${SITE}\",\"name\":\"${VLAN_NAME}\"}" -H 'Content-type: application/json' "http://127.0.0.1:5000/api/v1/vlans" &> $TMP
  cat $TMP
done
rm -f $TMP
