#!/bin/sh
network=$(docker network inspect kind -f "{{(index .IPAM.Config 0).Subnet}}" | cut -d '.' -f1,2)
# Based on this, generate a metallb address pool
rm -f $(dirname "$0")/metallb-ip-address-pool.yaml
cat << EOF >> $(dirname "$0")/metallb-ip-address-pool.yaml
apiVersion: metallb.io/v1beta1
kind: IPAddressPool
metadata:
  name: default
  namespace: metallb-system
spec:
    addresses:
    - ${network}.255.1-${network}.255.255
EOF
