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

# Create a new routing table if not already existing
echo "100 custom_routing" >> /etc/iproute2/rt_tables

# Add route to the custom table
sudo ip route add $TARGET_NETWORK dev tun0

# Apply the iptables rule to mark the packets
iptables -t nat -A POSTROUTING -s $TARGET_NETWORK ! -d $TARGET_NETWORK -j MASQUERADE

echo "Routing set for $DOMAIN to go through $TARGET_NETWORK"
