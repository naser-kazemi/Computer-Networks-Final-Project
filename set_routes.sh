#!/bin/bash

# Domain to be resolved
DOMAIN="neverssl.com"

# Network through which traffic should be routed
TARGET_NETWORK="172.16.0.0/24"

# Resolve the domain name to an IP address
IP_ADDRESS=$(dig +short $DOMAIN | tail -n1)

if [ -z "$IP_ADDRESS" ]; then
    echo "Failed to resolve domain: $DOMAIN"
    exit 1
fi

echo "Resolved IP for $DOMAIN is $IP_ADDRESS"

# Add route to the custom table
sudo ip route add $IP_ADDRESS dev tun0

# Apply the iptables rule to mark the packets
sudo iptables -t nat -A POSTROUTING -s $TARGET_NETWORK ! -d $TARGET_NETWORK -j MASQUERADE

echo "Routing set for $DOMAIN to go through $TARGET_NETWORK"
